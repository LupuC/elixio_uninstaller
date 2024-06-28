# Elixio Uninstaller

## Description

Elixio Uninstaller is a Python application built with tkinter for GUI, aimed at managing and uninstalling installed applications on Windows systems.

## Features

- **View Installed Applications**: Lists all installed applications fetched from Windows Registry.
- **Sort and Filter**: Applications can be sorted by name, size, or installation date.
- **Context Menu**: Right-click functionality to uninstall selected applications.
- **Check for Updates**: Automatically checks GitHub for updates and prompts the user to update if a newer version is available.
- **Custom Loading Indicator**: Provides visual feedback during data loading.

## Requirements

- Python 3.7+
- tkinter
- requests

## Installation
### Clonning the repo
1. Clone the repository:
```
git clone https://github.com/LupuC/elixio_uninstaller.git

cd elixio_uninstaller
```

Run the application:
```
python main.py
```
### Dwnloading the exec
2. Download the exec:
```
https://github.com/LupuC/elixio_uninstaller/releases
```

## Screenshots

![image](https://github.com/LupuC/elixio_uninstaller/assets/62475718/25a99f21-b4f9-4dcd-83ce-bcb8d8ae78a9)


## Known issues/ bugs:
1. Filters only works 1 way (sorting from a>z, 0 to 9 etc)
2. Total gigs from the bottom left, is not working properly
3. Sometimes,  when the app stars, it won't be on top of other apps.
4. **IMPORTANT** The app will be removed from the list, even if you press "No" on uninstall confirmation.


## How It Works

The application uses Python's tkinter library for the graphical interface and interacts with the Windows Registry to fetch installed application details. It includes functionality to check for updates from GitHub and allows uninstalling applications directly from the GUI.

## Contributing

Contributions are welcome! Please fork the repository and submit a pull request.

## License

This project is licensed under the MIT License - see the LICENSE file for details.

## Acknowledgments

- Custom tkinter widgets and appearance by customtkinter
- Loading indicator design inspired by LoadingIndicator
