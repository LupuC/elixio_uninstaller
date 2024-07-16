# Elixio Uninstaller

## Overview

Elixio Uninstaller is a sophisticated Windows application management tool developed in Python. It provides a user-friendly interface for viewing, sorting, and uninstalling applications, leveraging the power of the Windows Registry for accurate system information.

## Key Features

- **Comprehensive Application Inventory**: Displays a detailed list of installed applications, sourced directly from the Windows Registry.
- **Advanced Sorting and Filtering**: Enables efficient navigation through applications with customizable sorting by name, size, or installation date.
- **Intuitive Uninstall Process**: Streamlines application removal via a convenient right-click context menu.
- **Automatic Update Checks**: Implements GitHub integration for seamless version control and update notifications.
- **Responsive User Interface**: Features a custom loading indicator for enhanced user experience during data retrieval.

## Technical Requirements

- Python 3.7 or higher
- tkinter library
- requests library

## Installation Guide

### Option 1: Source Code Installation

1. Clone the repository:
   ```
   git clone https://github.com/LupuC/elixio_uninstaller.git
   cd elixio_uninstaller
   ```

2. Execute the application:
   ```
   python main.py
   ```

### Option 2: Executable Installation

Download the latest executable from our [GitHub Releases page](https://github.com/LupuC/elixio_uninstaller/releases).

## Visual Preview

![Elixio Uninstaller Interface](https://github.com/user-attachments/assets/4818b694-ea9d-4359-bfdd-6dd14da3524e)

## Current Limitations

- The update notification system is currently undergoing refinement to ensure optimal functionality.

## Technical Architecture

Elixio Uninstaller is built on Python's tkinter library for its graphical user interface. It interfaces with the Windows Registry to extract detailed information about installed applications. The application incorporates GitHub integration for version control and update management.

## Contribution Guidelines

We welcome contributions to enhance Elixio Uninstaller. Please fork the repository and submit pull requests for any improvements or bug fixes.

## Licensing

This project is distributed under the MIT License. For full details, please refer to the LICENSE file in the repository.

## Acknowledgements

- The customtkinter library for enhanced widget functionality and appearance.
- Inspiration for the loading indicator design drawn from the LoadingIndicator project.