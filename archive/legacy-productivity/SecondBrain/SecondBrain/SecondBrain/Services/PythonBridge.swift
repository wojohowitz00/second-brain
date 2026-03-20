//
//  PythonBridge.swift
//  SecondBrain
//

import Foundation

class PythonBridge {
    static let shared = PythonBridge()
    
    private func findScriptsPath(vaultPath: String? = nil) -> URL? {
        let fileManager = FileManager.default
        
        // Try 1: Use provided vault path
        if let vaultPath = vaultPath, !vaultPath.isEmpty {
            let scriptsPath = URL(fileURLWithPath: vaultPath).appendingPathComponent("_scripts")
            if fileManager.fileExists(atPath: scriptsPath.path) {
                return scriptsPath
            }
        }
        
        // Try 2: Standard vault location
        let homeDir = fileManager.homeDirectoryForCurrentUser
        let defaultVaultPath = homeDir.appendingPathComponent("SecondBrain")
        let defaultScriptsPath = defaultVaultPath.appendingPathComponent("_scripts")
        if fileManager.fileExists(atPath: defaultScriptsPath.path) {
            return defaultScriptsPath
        }
        
        // Try 3: Project directory (for development)
        if let projectRoot = findProjectRoot() {
            let projectScriptsPath = projectRoot.appendingPathComponent("_scripts")
            if fileManager.fileExists(atPath: projectScriptsPath.path) {
                return projectScriptsPath
            }
        }
        
        return nil
    }
    
    private func findProjectRoot() -> URL? {
        // Try to find the project root by looking for _scripts directory
        // Check common locations relative to the app bundle
        if let bundlePath = Bundle.main.resourcePath {
            var current = URL(fileURLWithPath: bundlePath)
            
            // Go up a few levels from the bundle
            for _ in 0..<5 {
                current = current.deletingLastPathComponent()
                let scriptsPath = current.appendingPathComponent("_scripts")
                if FileManager.default.fileExists(atPath: scriptsPath.path) {
                    return current
                }
            }
        }
        
        // Also try the workspace directory if we can detect it
        let workspacePath = "/Users/richardyu/PARA/1_projects/coding/second_brain"
        if FileManager.default.fileExists(atPath: workspacePath) {
            return URL(fileURLWithPath: workspacePath)
        }
        
        return nil
    }
    
    private func executeScriptWithSystemPython(scriptName: String, arguments: [String], environment: [String: String], vaultPath: String?, scriptsPath: URL, scriptURL: URL) -> Result<String, Error> {
        // Set up environment
        var env = ProcessInfo.processInfo.environment
        for (key, value) in environment {
            env[key] = value
        }
        env["PYTHONPATH"] = scriptsPath.path
        
        // Find system Python
        var pythonPaths: [String] = []
        
        // Check for venv in scripts directory first
        let venvPythonPath = scriptsPath.appendingPathComponent(".venv/bin/python3").path
        if FileManager.default.fileExists(atPath: venvPythonPath) {
            pythonPaths.append(venvPythonPath)
        }
        
        // Then check system Python locations
        pythonPaths.append(contentsOf: [
            "/usr/bin/python3",
            "/usr/local/bin/python3",
            "/opt/homebrew/bin/python3",
            "/Library/Frameworks/Python.framework/Versions/Current/bin/python3"
        ])
        
        var pythonPath: String?
        for path in pythonPaths {
            if FileManager.default.fileExists(atPath: path) {
                pythonPath = path
                break
            }
        }
        
        guard let pythonExecutable = pythonPath else {
            return .failure(PythonBridgeError.executionFailed("Python 3 not found. Please install Python 3.9+"))
        }
        
        let process = Process()
        process.executableURL = URL(fileURLWithPath: pythonExecutable)
        process.arguments = [scriptURL.path] + arguments
        process.currentDirectoryURL = scriptsPath
        process.environment = env
        
        // Capture output
        let pipe = Pipe()
        let errorPipe = Pipe()
        process.standardOutput = pipe
        process.standardError = errorPipe
        
        do {
            try process.run()
            process.waitUntilExit()
            
            let data = pipe.fileHandleForReading.readDataToEndOfFile()
            let errorData = errorPipe.fileHandleForReading.readDataToEndOfFile()
            
            if process.terminationStatus != 0 {
                let errorString = String(data: errorData, encoding: .utf8) ?? "Unknown error"
                return .failure(PythonBridgeError.executionFailed(errorString))
            }
            
            guard let output = String(data: data, encoding: .utf8) else {
                return .failure(PythonBridgeError.invalidOutput)
            }
            
            return .success(output)
        } catch {
            return .failure(error)
        }
    }
    
    func executeScript(_ scriptName: String, arguments: [String] = [], environment: [String: String] = [:], vaultPath: String? = nil) -> Result<String, Error> {
        guard let scriptsPath = findScriptsPath(vaultPath: vaultPath) else {
            return .failure(PythonBridgeError.scriptNotFound("_scripts directory not found"))
        }
        
        let scriptURL = scriptsPath.appendingPathComponent(scriptName)
        
        guard FileManager.default.fileExists(atPath: scriptURL.path) else {
            return .failure(PythonBridgeError.scriptNotFound(scriptName))
        }
        
        // Try to use uv first (preferred method)
        // Check common installation locations
        let homeDir = FileManager.default.homeDirectoryForCurrentUser.path
        let uvPaths = [
            "/opt/homebrew/bin/uv",
            "/usr/local/bin/uv",
            "/usr/bin/uv",
            "\(homeDir)/.cargo/bin/uv",  // uv installer default location
            "\(homeDir)/.local/bin/uv"    // Alternative location
        ]
        
        var uvPath: String?
        for path in uvPaths {
            if FileManager.default.fileExists(atPath: path) {
                uvPath = path
                break
            }
        }
        
        // Set up environment first - start with clean environment to ensure variables are passed
        var env: [String: String] = [:]
        
        // Copy current process environment
        let currentEnv = ProcessInfo.processInfo.environment
        for (key, value) in currentEnv {
            env[key] = value
        }
        
        // Override/add provided environment variables (these take precedence)
        for (key, value) in environment {
            env[key] = value
        }
        
        // Set PYTHONPATH to scripts directory for imports
        env["PYTHONPATH"] = scriptsPath.path
        
        let process = Process()
        
        if let uv = uvPath {
            // Use uv run to execute the script (handles venv automatically)
            // First check if venv exists, if not uv will create it
            let venvPath = scriptsPath.appendingPathComponent(".venv").path
            let venvExists = FileManager.default.fileExists(atPath: venvPath)
            
            // Use uv run python script.py args... runs the script in the venv
            process.executableURL = URL(fileURLWithPath: uv)
            // Use absolute path to script for uv
            // Add --python flag to ensure we use a proper Python installation
            if venvExists {
                process.arguments = ["run", "python", scriptURL.path] + arguments
            } else {
                // If venv doesn't exist, uv will create it, but we should ensure Python is available
                process.arguments = ["run", "--python", "3.11", "python", scriptURL.path] + arguments
            }
            process.currentDirectoryURL = scriptsPath
        } else {
            // Fallback to direct Python execution
            // First, check for virtual environment in scripts directory
            var pythonPaths: [String] = []
            
            // Check for venv in scripts directory
            let venvPythonPath = scriptsPath.appendingPathComponent(".venv/bin/python3").path
            if FileManager.default.fileExists(atPath: venvPythonPath) {
                pythonPaths.append(venvPythonPath)
            }
            
            // Then check system Python locations
            pythonPaths.append(contentsOf: [
                "/usr/bin/python3",
                "/usr/local/bin/python3",
                "/opt/homebrew/bin/python3",
                "/Library/Frameworks/Python.framework/Versions/Current/bin/python3"
            ])
            
            var pythonPath: String?
            for path in pythonPaths {
                if FileManager.default.fileExists(atPath: path) {
                    pythonPath = path
                    break
                }
            }
            
            guard let pythonExecutable = pythonPath else {
                return .failure(PythonBridgeError.executionFailed("Python 3 not found. Please install Python 3.9+ or install uv: curl -LsSf https://astral.sh/uv/install.sh | sh"))
            }
            
            process.executableURL = URL(fileURLWithPath: pythonExecutable)
            process.arguments = [scriptURL.path] + arguments
            // Set working directory to scripts path so relative imports work
            process.currentDirectoryURL = scriptsPath
        }
        
        // Apply environment to process
        process.environment = env
        
        // Capture output
        let pipe = Pipe()
        let errorPipe = Pipe()
        process.standardOutput = pipe
        process.standardError = errorPipe
        
        do {
            try process.run()
            process.waitUntilExit()
            
            let data = pipe.fileHandleForReading.readDataToEndOfFile()
            let errorData = errorPipe.fileHandleForReading.readDataToEndOfFile()
            
            if process.terminationStatus != 0 {
                let errorString = String(data: errorData, encoding: .utf8) ?? "Unknown error"
                
                // Check if this is a Python installation error (encodings missing, etc.)
                // If so and we used uv, fall back to system Python
                if uvPath != nil && (errorString.contains("encodings") || 
                                     errorString.contains("platform independent libraries") ||
                                     errorString.contains("Fatal Python error")) {
                    // Retry with system Python instead
                    return executeScriptWithSystemPython(scriptName: scriptName, 
                                                         arguments: arguments, 
                                                         environment: environment, 
                                                         vaultPath: vaultPath,
                                                         scriptsPath: scriptsPath,
                                                         scriptURL: scriptURL)
                }
                
                return .failure(PythonBridgeError.executionFailed(errorString))
            }
            
            guard let output = String(data: data, encoding: .utf8) else {
                return .failure(PythonBridgeError.invalidOutput)
            }
            
            return .success(output)
        } catch {
            return .failure(error)
        }
    }
    
    func executeScriptJSON<T: Decodable>(_ scriptName: String, arguments: [String] = [], environment: [String: String] = [:], vaultPath: String? = nil, as type: T.Type) -> Result<T, Error> {
        let result = executeScript(scriptName, arguments: arguments + ["--json-output"], environment: environment, vaultPath: vaultPath)
        
        switch result {
        case .success(let output):
            guard let data = output.data(using: .utf8) else {
                return .failure(PythonBridgeError.invalidJSON)
            }
            
            do {
                let decoder = JSONDecoder()
                decoder.dateDecodingStrategy = .iso8601
                let decoded = try decoder.decode(type, from: data)
                return .success(decoded)
            } catch {
                return .failure(PythonBridgeError.jsonDecodingFailed(error))
            }
        case .failure(let error):
            return .failure(error)
        }
    }
}

enum PythonBridgeError: LocalizedError {
    case scriptNotFound(String)
    case executionFailed(String)
    case invalidOutput
    case invalidJSON
    case jsonDecodingFailed(Error)
    
    var errorDescription: String? {
        switch self {
        case .scriptNotFound(let name):
            return "Python script not found: \(name)"
        case .executionFailed(let message):
            return "Script execution failed: \(message)"
        case .invalidOutput:
            return "Invalid script output"
        case .invalidJSON:
            return "Invalid JSON output"
        case .jsonDecodingFailed(let error):
            return "JSON decoding failed: \(error.localizedDescription)"
        }
    }
}
