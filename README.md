# 🔍 LustLens - Advanced Image Search & Scraper

<div align="center">

![Python](https://img.shields.io/badge/Python-3.8+-3776AB?style=for-the-badge&logo=python&logoColor=white)
![Web Scraping](https://img.shields.io/badge/Web-Scraping-green?style=for-the-badge)
![OSINT](https://img.shields.io/badge/OSINT-Tool-red?style=for-the-badge)

**Multi-threaded image search engine with automated gallery generation**

[Features](#-features) • [Installation](#-installation) • [Usage](#-usage) • [Legal](#-legal-disclaimer) • [Configuration](#-configuration)

</div>

---

## ⚠️ LEGAL DISCLAIMER

**READ THIS CAREFULLY BEFORE USING THIS TOOL**

This software is a web scraping tool designed for **legitimate research, OSINT investigations, and authorized data collection ONLY**.

### Legal Use Cases:
- ✅ Digital forensics and OSINT research
- ✅ Academic research with proper authorization
- ✅ Personal archiving of public domain content
- ✅ Security research and penetration testing
- ✅ Data analysis and machine learning dataset creation (with proper licensing)

### PROHIBITED Uses:
- ❌ Downloading copyrighted material without permission
- ❌ Harassment, stalking, or invasion of privacy
- ❌ Creating or distributing non-consensual intimate images
- ❌ Violating terms of service of search engines
- ❌ Commercial use without proper licensing
- ❌ Any illegal activity under your jurisdiction

### User Responsibilities:
1. **Respect copyright laws** - Only download content you have rights to use
2. **Respect privacy** - Do not use for stalking or harassment
3. **Follow ToS** - Respect rate limits and terms of service
4. **Legal compliance** - Ensure your use complies with local laws
5. **Ethical use** - Configure keywords responsibly

**The author disclaims ALL responsibility for misuse. Users are SOLELY responsible for their actions and must comply with all applicable laws.**

---

## 📋 Overview

LustLens is a powerful Python-based image search and scraping tool that automates the process of collecting images from search engines based on customizable keywords. It features multi-threaded downloads, intelligent duplicate detection, automatic gallery generation, and advanced session management.

**Key Capabilities:**
- Multi-source image aggregation (Bing Images)
- Parallel processing with configurable thread pools
- Smart duplicate detection via MD5 hashing
- Automatic HTML gallery generation
- Resolution filtering
- Session rotation and rate limiting
- Encrypted activity logging

## ✨ Features

### 🚀 Advanced Search Engine

**Multi-Threaded Architecture:**
- Concurrent query processing (6 threads)
- Parallel image downloads (8 threads)
- Asynchronous HTTP requests
- Smart request throttling

**Intelligent Scraping:**
- Multiple URL extraction patterns
- JSON metadata parsing
- Regex-based image discovery
- CAPTCHA detection and retry logic
- User-Agent rotation (6+ profiles)

**Search Engine Integration:**
- Bing Images API
- Advanced query parameters
- SafeSearch toggle
- Large image filtering
- Regional preferences

### 🖼️ Image Processing

**Quality Control:**
- Minimum resolution filtering (default: 500x500)
- Content-Type validation
- Image format verification (JPEG, PNG, GIF, WebP)
- Corrupted file detection
- Size validation

**Duplicate Prevention:**
- MD5 hash-based deduplication
- Cross-session duplicate tracking
- Memory-efficient hash storage
- Automatic skip of existing files

### 📊 Gallery Generation

**Professional HTML Gallery:**
- Responsive grid layout (CSS Grid)
- Lightbox modal viewer
- Keyboard navigation (arrows, ESC)
- Click-to-zoom functionality
- Drag-to-pan when zoomed
- Mouse wheel zoom control
- Mobile-responsive design
- Lazy loading optimization
- Image counter overlay

**Gallery Features:**
- Clean, modern UI
- Fast loading times
- Touch gesture support
- Full-screen viewing
- Sequential navigation
- Image metadata display

### 🔒 Privacy & Security

**Activity Logging:**
- AES-256 encrypted IP logging
- Timestamped session records
- Separate key storage
- Base64 encoded data
- Crypto-secure random keys

**Session Management:**
- Domain-specific sessions
- Cookie persistence
- Header customization
- Referer handling
- Session rotation on errors

**Rate Limiting:**
- Configurable request delays
- Exponential backoff
- Retry mechanisms (3 attempts)
- Timeout protection (20s)
- CAPTCHA avoidance

### ⚙️ Configuration System

**Customizable Settings:**
- Minimum image resolution
- Request delay ranges
- SafeSearch filter
- Thread pool sizes
- Timeout values
- Keyword lists

**User-Friendly Interface:**
- Interactive menu system
- Real-time progress bars (tqdm)
- Colored terminal output
- Clear status messages
- Configuration persistence

## 🚀 Installation

### Prerequisites

**System Requirements:**
- Python 3.8 or higher
- Internet connection
- 2GB+ RAM recommended
- Modern terminal with UTF-8 support

### Dependencies Installation

```bash
# Clone repository
git clone https://github.com/sofiaelena777/lustlens.git
cd lustlens

# Install dependencies
pip install -r requirements.txt
```

**Required Packages:**
- `requests` - HTTP library
- `beautifulsoup4` - HTML parsing
- `Pillow` - Image processing
- `pycryptodome` - Encryption
- `tqdm` - Progress bars
- `aiohttp` - Async HTTP

### Quick Start

```bash
# Run the tool
python3 lustlens.py
```

## 📖 Usage

### Basic Workflow

1. **Launch Tool:**
```bash
python3 lustlens.py
```

2. **Main Menu:**
```
1. Start image search
2. Settings
0. Exit
```

3. **Configure Search:**
- Enter model/subject name
- Choose destination folder
- Tool automatically uses configured keywords

4. **Monitor Progress:**
- Real-time progress bar
- Image counter updates
- Status messages

5. **View Results:**
- Open generated `gallery.html`
- Browse images in browser
- Navigate with keyboard/mouse

### Configuration Options

**Settings Menu:**

**1. Minimum Resolution**
```
Default: 500x500 pixels
Configure: Enter custom width and height
Purpose: Filter low-quality images
```

**2. Request Delay**
```
Default: 1-3 seconds
Configure: Set min/max delay range
Purpose: Avoid rate limiting and bans
```

**3. SafeSearch Filter**
```
Default: OFF
Options: Enable (filtered) / Disable (no restrictions)
Purpose: Control content filtering
```

### Keyword Configuration

**Edit `PALAVRAS_CHAVE_INTERNAS` list:**

```python
PALAVRAS_CHAVE_INTERNAS = [
    "portrait", "photoshoot", "modeling", 
    "professional", "studio", "editorial",
    "fashion", "glamour", "artistic"
]
```

**Keyword Guidelines:**
- Use specific, descriptive terms
- Combine subject + context
- Avoid ambiguous words
- Test with small batches first
- Review results and adjust

### Advanced Usage

**Custom Destination Folder:**
```python
# When prompted:
[>] Enter destination folder path: /path/to/custom/folder
```

**Batch Processing:**
```python
# Create script for multiple subjects
subjects = ["subject1", "subject2", "subject3"]
for subject in subjects:
    # Run search for each
```

## 🗂️ Output Structure

### Directory Layout

```
destination_folder/
└── subject_name/
    ├── gallery.html          # Interactive gallery
    ├── abc123def456.jpg      # Image (MD5 hash)
    ├── 789ghi012jkl.jpg      # Image (MD5 hash)
    └── ...
```

### Gallery Features

**Viewing Experience:**
- Grid layout with hover effects
- Click image to open lightbox
- Arrow keys for navigation
- Click image in lightbox to zoom
- Drag to pan when zoomed
- Mouse wheel to zoom in/out
- ESC to close lightbox
- Mobile touch support

### Log Files

**Location:** System temp directory + `LustLens_Logs/`

**Files:**
- `log_ips.txt` - Encrypted IP logs
- `key_YYYYMMDD_HHMMSS.key` - Decryption keys
- `log_crypto.txt` - Encryption details

## 🔧 Technical Details

### Architecture

**Threading Model:**
```
Main Thread
├── Query Processor (6 threads)
│   ├── Bing API Requests
│   └── HTML Parsing
└── Image Downloader (8 threads)
    ├── URL Validation
    ├── Image Download
    └── Hash & Save
```

**Session Management:**
```python
SessionManager
├── Domain-specific sessions
├── Cookie persistence
├── Header rotation
└── Session recycling on errors
```

### Performance Optimization

**Parallelization:**
- Thread pool executors
- Concurrent futures
- Async HTTP requests
- Batch processing

**Memory Efficiency:**
- Stream downloads (chunked)
- Hash-based deduplication
- Lazy image loading in gallery
- Garbage collection

**Network Optimization:**
- Connection pooling
- Keep-alive headers
- Compression support (gzip, br, zstd)
- Smart retry logic

### Hash-Based Deduplication

```python
def hash_imagem(conteudo):
    return hashlib.md5(conteudo).hexdigest()
```

**Benefits:**
- Content-based comparison
- Filename-independent
- Fast lookup (set)
- Cross-session persistence

## 🛡️ Security Features

### Encryption System

**AES-256-CBC Encryption:**
```python
# IP address encryption
Key: 256-bit random
Mode: CBC (Cipher Block Chaining)
IV: 128-bit random
Padding: PKCS#7
```

**Key Management:**
- Separate key files per session
- Timestamped key storage
- Base64 encoded for transport
- Secure random generation

### Privacy Protection

**User-Agent Rotation:**
- 6+ modern browser profiles
- Chrome, Firefox, Edge, Safari
- Recent version strings
- Platform-specific headers

**Request Anonymization:**
- No persistent identifiers
- Cookie isolation per domain
- Referer header management
- DNT (Do Not Track) enabled

## 🐛 Troubleshooting

### No Images Found

**Possible causes:**
- Keywords too specific
- SafeSearch blocking results
- Rate limiting active
- Network issues

**Solutions:**
```bash
# 1. Check internet connection
ping bing.com

# 2. Adjust keywords
# Edit PALAVRAS_CHAVE_INTERNAS with broader terms

# 3. Increase delays
# Settings > Request delay > 3-6 seconds

# 4. Disable SafeSearch
# Settings > SafeSearch > Disable
```

### CAPTCHA Detected

**Signs:**
- "Captcha detected" in output
- Very few results
- HTTP 429 errors

**Solutions:**
- Increase request delays
- Wait 10-30 minutes
- Use VPN/proxy (manual setup)
- Reduce concurrent threads

### Download Failures

**Common errors:**
```
Connection timeout
SSL certificate error
HTTP 403 Forbidden
Invalid image format
```

**Fixes:**
```python
# Increase timeout
TIMEOUT_REQUEST = 30

# More retries
MAX_TENTATIVAS = 5

# Adjust user agents
# Add custom headers
```

### Gallery Not Loading

**Issues:**
- Images not displaying
- JavaScript errors
- Blank gallery

**Solutions:**
```bash
# 1. Check image files exist
ls destination_folder/subject_name/*.jpg

# 2. Verify gallery.html exists
cat destination_folder/subject_name/gallery.html

# 3. Open in different browser
# Try Chrome, Firefox, Edge

# 4. Check browser console
# F12 > Console tab
```

## 📊 Performance Tuning

### Optimal Settings

**Fast Search (may trigger rate limits):**
```python
MAX_THREADS_CONSULTAS = 8
MAX_THREADS_IMAGENS = 12
DELAY_REQUESTS = (0.5, 1.5)
```

**Balanced (recommended):**
```python
MAX_THREADS_CONSULTAS = 6
MAX_THREADS_IMAGENS = 8
DELAY_REQUESTS = (1, 3)
```

**Safe (slow but reliable):**
```python
MAX_THREADS_CONSULTAS = 3
MAX_THREADS_IMAGENS = 4
DELAY_REQUESTS = (3, 6)
```

### Resource Usage

**Typical:**
- CPU: 10-30% (multi-core)
- RAM: 200-500 MB
- Network: 1-10 Mbps
- Disk: Variable (image sizes)

**High Load:**
- CPU: 40-60%
- RAM: 500-1000 MB
- Network: 10-50 Mbps

## 🤝 Contributing

Contributions welcome! Areas for improvement:

- [ ] Additional search engines (Google, DuckDuckGo, Yandex)
- [ ] Proxy/VPN integration
- [ ] GUI interface
- [ ] Database storage (SQLite)
- [ ] Image metadata extraction
- [ ] AI-based content classification
- [ ] Batch keyword templates
- [ ] Cloud storage integration
- [ ] API endpoint creation

## 📜 License

MIT License

```
Copyright (c) 2024 sofiaelena777

Permission is hereby granted, free of charge, to any person obtaining a copy
of this software and associated documentation files (the "Software"), to deal
in the Software without restriction, including without limitation the rights
to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
copies of the Software, and to permit persons to whom the Software is
furnished to do so.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT.
```

## 👤 Author

**sofiaelena777**

- GitHub: [@sofiaelena777](https://github.com/sofiaelena777)

## 🙏 Acknowledgments

- BeautifulSoup4 developers
- Python Requests library
- Pillow imaging library
- Open source community

---

<div align="center">

**⚠️ Use Responsibly | 🔒 Respect Privacy | 📖 Follow Laws**

**Configure keywords appropriately for your legal use case**

Made with ❤️ by sofiaelena777

</div>
