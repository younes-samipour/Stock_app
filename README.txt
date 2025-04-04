# Stock Management Application
Version 1.0

## Overview
This is a comprehensive stock management application designed to help users monitor, analyze, and manage their stock portfolio. The application provides real-time market data, portfolio tracking, watchlist functionality, and stock data downloads. Built with Python and Tkinter, it offers a robust platform for both novice and experienced investors.

## Features

### 1. Market Page
- Real-time stock market data display with automatic 60-second updates
- Advanced stock filtering and search capabilities:
  * Filter by price range
  * Filter by volume
  * Filter by market cap
  * Search by symbol or company name
- Market indices tracking with visual indicators
- Comprehensive news and announcements section with categorization
- Auto-refresh functionality (every 60 seconds)
- Customizable view with multiple tabs:
  * Stocks listing with sortable columns
  * Market indices with trend indicators
  * Latest news with category filters
- Export functionality for data analysis

### 2. Portfolio Management
- Track multiple stock positions with detailed information:
  * Purchase price and date
  * Current market value
  * Quantity
  * Commission costs
  * Dividends received
- Real-time portfolio valuation with currency conversion
- Sophisticated performance analytics:
  * Profit/Loss tracking (realized and unrealized)
  * Position weights and diversification metrics
  * Risk metrics including Beta and Volatility
  * Sector allocation analysis
- Detailed transaction history with filtering options
- Portfolio rebalancing suggestions based on:
  * Risk tolerance
  * Sector allocation
  * Market conditions
- Comprehensive reporting capabilities:
  * YTD (Year to Date) performance
  * MTD (Month to Date) analysis
  * Custom period selection
  * PDF export functionality
  * Performance comparison with market indices

### 3. Watchlist
- Highly customizable stock watchlist with multiple views
- Sophisticated alert system:
  * Price threshold alerts (upper and lower bounds)
  * Volume spike alerts
  * Technical indicator alerts
  * Percentage change alerts
- Real-time updates with visual indicators
- Quick access to detailed stock information:
  * Technical analysis charts
  * Fundamental data
  * News feed
- Intuitive right-click context menu for quick actions:
  * Add to portfolio
  * Set alerts
  * View detailed analysis
- Color-coded price changes with customizable thresholds
- Automatic updates every minute with manual refresh option
- Multiple watchlist support for different strategies

### 4. Download Center
- Efficient stock data download system for multiple symbols
- Three comprehensive categories of stocks:
  * Bourse stocks (main market)
  * Farabourse stocks (OTC market)
  * Selected stocks (user-defined lists)
- Detailed progress tracking for downloads:
  * Progress bar for each download
  * Estimated time remaining
  * Download speed
  * Success/failure status
- Searchable download history with filtering
- Bulk download capability with priority settings
- Data validation and error checking
- Export options in multiple formats:
  * CSV
  * Excel
  * JSON
  * SQL

### 5. Settings
- Comprehensive API configuration:
  * Multiple API endpoint support
  * API key management
  * Request rate limiting
  * Timeout settings
- Advanced database settings:
  * Backup configuration
  * Data retention policies
  * Performance optimization
- Customizable user preferences:
  * Theme selection
  * Language settings
  * Date and time format
  * Number format
- Configurable alert thresholds:
  * Price movement
  * Volume changes
  * Technical indicators
- System performance settings:
  * Update frequency
  * Cache size
  * Log level

## Technical Details

### Database Structure
The application uses SQLite database with the following main tables:
- settings: Stores application configuration and user preferences
  * API configurations
  * User interface settings
  * Alert thresholds
  * System parameters
- portfolio: Manages portfolio positions and transactions
  * Stock positions
  * Transaction history
  * Performance metrics
  * Cost basis calculations
- watchlist: Stores watched stocks and alert settings
  * Watch items
  * Alert configurations
  * Custom notes
  * Priority levels
- stock_data: Contains downloaded stock information
  * Price history
  * Volume data
  * Company information
  * Technical indicators

### Threading
- Sophisticated background threads for data updates:
  * Market data updates
  * Portfolio calculations
  * Alert monitoring
- Main thread dedicated to UI updates for smooth operation
- Thread-safe operations for database access with connection pooling
- Queue-based task management system
- Deadlock prevention mechanisms

### User Interface
- Modern Tkinter interface with custom styling
- Efficient tabbed navigation system
- Responsive design that adapts to window size
- Comprehensive Persian language support
- Right-to-left (RTL) layout optimization
- Custom widgets and controls
- Keyboard shortcuts for power users

## Installation Guide
1. System Requirements Check:
   * Verify Python 3.7+ installation
   * Check available RAM (4GB minimum)
   * Ensure internet connectivity
   * Verify screen resolution

2. Dependencies Installation:
   ```bash
   pip install -r requirements.txt
   ```

3. Database Setup:
   ```bash
   python setup_database.py
   ```

4. Configuration:
   * Copy config.example.ini to config.ini
   * Update API credentials
   * Set initial preferences

## Persian Guide / راهنمای فارسی

### راهنمای نصب و راه‌اندازی
1. نصب برنامه:
   * دانلود فایل‌های برنامه
   * نصب پایتون نسخه 3.7 یا بالاتر
   * نصب کتابخانه‌های مورد نیاز

2. تنظیمات اولیه:
   * پیکربندی API ها در بخش تنظیمات
   * وارد کردن اطلاعات کاربری
   * تنظیم پارامترهای مورد نیاز

### امکانات اصلی برنامه
* نمایش اطلاعات لحظه‌ای بازار
* مدیریت پرتفوی سهام
* دیده‌بان سهام با هشدارهای قیمتی
* دانلود اطلاعات سهام‌ها
* گزارش‌گیری پیشرفته

### نکات مهم
* پشتیبان‌گیری منظم از دیتابیس
* بروزرسانی تنظیمات API
* مدیریت هشدارها
* بررسی دوره‌ای عملکرد سیستم

برای اطلاعات بیشتر و پشتیبانی با تیم توسعه تماس بگیر
@younes1345 in telegram.me
Last updated: 2025 