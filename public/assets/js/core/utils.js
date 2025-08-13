/**
 * Utility functions for ASIA.fr Agent Frontend
 */

// Get configuration from global scope (only if not already defined)
if (typeof DEBUG_CONFIG === 'undefined') {
    const DEBUG_CONFIG = window.DEBUG_CONFIG || {
        ENABLED: true,
        LOG_PREFIX: '[ASIA]'
    };
    window.DEBUG_CONFIG = DEBUG_CONFIG;
}

// Only create classes if they don't exist
if (typeof Logger === 'undefined') {
    /**
     * Logger utility
     */
    class Logger {
        static log(level, message, ...args) {
            if (!DEBUG_CONFIG.ENABLED) return;
            
            const prefix = DEBUG_CONFIG.LOG_PREFIX;
            const timestamp = new Date().toISOString();
            
            switch (level) {
                case 'debug':
                    console.debug(`${prefix} [${timestamp}] ${message}`, ...args);
                    break;
                case 'info':
                    console.info(`${prefix} [${timestamp}] ${message}`, ...args);
                    break;
                case 'warn':
                    console.warn(`${prefix} [${timestamp}] ${message}`, ...args);
                    break;
                case 'error':
                    console.error(`${prefix} [${timestamp}] ${message}`, ...args);
                    break;
                default:
                    console.log(`${prefix} [${timestamp}] ${message}`, ...args);
            }
        }
        
        static debug(message, ...args) {
            this.log('debug', message, ...args);
        }
        
        static info(message, ...args) {
            this.log('info', message, ...args);
        }
        
        static warn(message, ...args) {
            this.log('warn', message, ...args);
        }
        
        static error(message, ...args) {
            this.log('error', message, ...args);
        }
    }

    // Make available globally
    window.Logger = Logger;
}

if (typeof DOMUtils === 'undefined') {
    /**
     * DOM utilities
     */
    class DOMUtils {
        static getElement(selector) {
            return document.querySelector(selector);
        }
        
        static getElements(selector) {
            return document.querySelectorAll(selector);
        }
        
        static createElement(tag, className = '', innerHTML = '') {
            const element = document.createElement(tag);
            if (className) element.className = className;
            if (innerHTML) element.innerHTML = innerHTML;
            return element;
        }
        
        static addClass(element, className) {
            if (element && element.classList) {
                element.classList.add(className);
            }
        }
        
        static removeClass(element, className) {
            if (element && element.classList) {
                element.classList.remove(className);
            }
        }
        
        static toggleClass(element, className) {
            if (element && element.classList) {
                element.classList.toggle(className);
            }
        }
        
        static setAttribute(element, name, value) {
            if (element) {
                element.setAttribute(name, value);
            }
        }
        
        static getAttribute(element, name) {
            return element ? element.getAttribute(name) : null;
        }
    }

    // Make available globally
    window.DOMUtils = DOMUtils;
}

if (typeof StorageUtils === 'undefined') {
    /**
     * Storage utilities
     */
    class StorageUtils {
        static set(key, value) {
            try {
                localStorage.setItem(key, JSON.stringify(value));
                return true;
            } catch (error) {
                Logger.error('Failed to save to localStorage:', error);
                return false;
            }
        }
        
        static get(key, defaultValue = null) {
            try {
                const item = localStorage.getItem(key);
                return item ? JSON.parse(item) : defaultValue;
            } catch (error) {
                Logger.error('Failed to read from localStorage:', error);
                return defaultValue;
            }
        }
        
        static remove(key) {
            try {
                localStorage.removeItem(key);
                return true;
            } catch (error) {
                Logger.error('Failed to remove from localStorage:', error);
                return false;
            }
        }
        
        static clear() {
            try {
                localStorage.clear();
                return true;
            } catch (error) {
                Logger.error('Failed to clear localStorage:', error);
                return false;
            }
        }
    }

    // Make available globally
    window.StorageUtils = StorageUtils;
}

if (typeof StringUtils === 'undefined') {
    /**
     * String utilities
     */
    class StringUtils {
        static truncate(str, maxLength, suffix = '...') {
            if (str.length <= maxLength) return str;
            return str.substring(0, maxLength - suffix.length) + suffix;
        }
        
        static capitalize(str) {
            return str.charAt(0).toUpperCase() + str.slice(1);
        }
        
        static slugify(str) {
            return str
                .toLowerCase()
                .replace(/[^a-z0-9 -]/g, '')
                .replace(/\s+/g, '-')
                .replace(/-+/g, '-')
                .trim('-');
        }
        
        static escapeHtml(str) {
            const div = document.createElement('div');
            div.textContent = str;
            return div.innerHTML;
        }
    }

    // Make available globally
    window.StringUtils = StringUtils;
}

if (typeof DateUtils === 'undefined') {
    /**
     * Date utilities
     */
    class DateUtils {
        static formatDate(date, format = 'YYYY-MM-DD') {
            const d = new Date(date);
            const year = d.getFullYear();
            const month = String(d.getMonth() + 1).padStart(2, '0');
            const day = String(d.getDate()).padStart(2, '0');
            
            return format
                .replace('YYYY', year)
                .replace('MM', month)
                .replace('DD', day);
        }
        
        static formatDuration(days) {
            if (days === 1) return '1 jour';
            return `${days} jours`;
        }
        
        static isToday(date) {
            const today = new Date();
            const d = new Date(date);
            return d.toDateString() === today.toDateString();
        }
    }

    // Make available globally
    window.DateUtils = DateUtils;
}

if (typeof AnimationUtils === 'undefined') {
    /**
     * Animation utilities
     */
    class AnimationUtils {
        static fadeIn(element, duration = 300) {
            if (!element) return;
            
            element.style.opacity = '0';
            element.style.display = 'block';
            
            let start = null;
            const animate = (timestamp) => {
                if (!start) start = timestamp;
                const progress = timestamp - start;
                const opacity = Math.min(progress / duration, 1);
                
                element.style.opacity = opacity;
                
                if (progress < duration) {
                    requestAnimationFrame(animate);
                }
            };
            
            requestAnimationFrame(animate);
        }
        
        static fadeOut(element, duration = 300) {
            if (!element) return;
            
            let start = null;
            const animate = (timestamp) => {
                if (!start) start = timestamp;
                const progress = timestamp - start;
                const opacity = Math.max(1 - (progress / duration), 0);
                
                element.style.opacity = opacity;
                
                if (progress < duration) {
                    requestAnimationFrame(animate);
                } else {
                    element.style.display = 'none';
                }
            };
            
            requestAnimationFrame(animate);
        }
        
        static slideDown(element, duration = 300) {
            if (!element) return;
            
            element.style.height = '0';
            element.style.overflow = 'hidden';
            element.style.display = 'block';
            
            const targetHeight = element.scrollHeight;
            let start = null;
            
            const animate = (timestamp) => {
                if (!start) start = timestamp;
                const progress = timestamp - start;
                const height = Math.min((progress / duration) * targetHeight, targetHeight);
                
                element.style.height = `${height}px`;
                
                if (progress < duration) {
                    requestAnimationFrame(animate);
                } else {
                    element.style.height = 'auto';
                    element.style.overflow = 'visible';
                }
            };
            
            requestAnimationFrame(animate);
        }
    }

    // Make available globally
    window.AnimationUtils = AnimationUtils;
}

if (typeof ValidationUtils === 'undefined') {
    /**
     * Validation utilities
     */
    class ValidationUtils {
        static isValidEmail(email) {
            const emailRegex = /^[^\s@]+@[^\s@]+\.[^\s@]+$/;
            return emailRegex.test(email);
        }
        
        static isValidPhone(phone) {
            const phoneRegex = /^[\+]?[1-9][\d]{0,15}$/;
            return phoneRegex.test(phone.replace(/\s/g, ''));
        }
        
        static isValidDate(date) {
            const d = new Date(date);
            return d instanceof Date && !isNaN(d);
        }
        
        static isNotEmpty(value) {
            return value !== null && value !== undefined && value.toString().trim() !== '';
        }
    }

    // Make available globally
    window.ValidationUtils = ValidationUtils;
} 