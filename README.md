# Second Brain

A unified repository containing both the Python backend and iOS app for the Second Brain project.

## Project Structure

```
second-brain/
├── backend/          # Python backend (Slack + Obsidian integration)
│   ├── _scripts/     # Python automation scripts
│   ├── _templates/   # Markdown templates
│   ├── tasks/        # Task tracking
│   ├── README.md     # Backend-specific documentation
│   └── setup.sh      # Setup script
│
├── ios/              # iOS application
│   ├── SecondBrain.xcodeproj/
│   ├── SecondBrain/  # Swift source files
│   └── Tests/
│
└── docs/             # Documentation
    ├── README.md     # System overview
    └── GUIDE.md      # Complete setup guide
```

## Getting Started

### Backend Setup
```bash
cd backend
./setup.sh
```

See `backend/README.md` for detailed backend documentation.

### iOS Development
Open `ios/SecondBrain.xcodeproj` in Xcode.

### Documentation
See `docs/` for comprehensive guides on the Second Brain system architecture and setup.

## Git History

This repository consolidates two previously separate projects:
- Python backend (13+ commits, active development through Jan 2026)
- iOS app (initial development Jan 2026)

The reorganization commit preserves the full history of both projects.
