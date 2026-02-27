# Yoto Icons Alternative UI

This project is an alternative user interface for browsing, searching, and downloading Yoto icons. It is inspired by  [yotoicons.com](https://yotoicons.com) and uses the icons and metadata for the original concept and data.

## Features

- Search icons by category or tags
- Select multiple icons and download them in bulk
- View icon details and tags via tooltips
- Responsive design for desktop and mobile

## Installation

1. **Clone the repository:**
   ```
   git clone https://github.com/tomekent/yotoicons.git
   cd yotoicons
   ```

2. **Install dependencies using uv:**
   ```
   uv pip install -r requirements.lock
   ```

3. **Run the server:**
   ```
   uvicorn app.main:app --reload
   ```

4. **Access the UI:**
   Open your browser and go to `http://localhost:8000`.

## Credits

- Original concept and data: [yotoicons.com](https://yotoicons.com)

## License

This project is provided for educational and personal use. Please respect the original icon creators and [yotoicons.com](https://yotoicons.com).