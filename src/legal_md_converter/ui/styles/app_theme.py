"""
Application theme for Legal-MD-Converter.

Provides consistent styling across the application using Qt stylesheets.
"""


class AppTheme:
    """Centralized theme management for the application."""
    
    # Color palette
    COLORS = {
        'primary': '#2196F3',
        'primary_dark': '#1976D2',
        'primary_light': '#BBDEFB',
        'secondary': '#4CAF50',
        'accent': '#FF9800',
        'background': '#FFFFFF',
        'background_light': '#F5F5F5',
        'background_dark': '#E0E0E0',
        'text_primary': '#212121',
        'text_secondary': '#757575',
        'text_disabled': '#BDBDBD',
        'border': '#E0E0E0',
        'border_dark': '#9E9E9E',
        'success': '#4CAF50',
        'warning': '#FF9800',
        'error': '#F44336',
        'info': '#2196F3',
    }
    
    @classmethod
    def get_main_stylesheet(cls) -> str:
        """
        Get the main application stylesheet.
        
        Returns:
            str: Complete Qt stylesheet for the application
        """
        return f'''
            /* Main Window */
            QMainWindow {{
                background-color: {cls.COLORS['background']};
            }}
            
            /* Menu Bar */
            QMenuBar {{
                background-color: {cls.COLORS['background']};
                border-bottom: 1px solid {cls.COLORS['border']};
                padding: 2px;
            }}
            
            QMenuBar::item {{
                background-color: transparent;
                padding: 8px 12px;
                color: {cls.COLORS['text_primary']};
            }}
            
            QMenuBar::item:selected {{
                background-color: {cls.COLORS['primary_light']};
            }}
            
            QMenuBar::item:pressed {{
                background-color: {cls.COLORS['primary']};
                color: {cls.COLORS['background']};
            }}
            
            /* Menus */
            QMenu {{
                background-color: {cls.COLORS['background']};
                border: 1px solid {cls.COLORS['border']};
                border-radius: 4px;
                padding: 5px;
            }}
            
            QMenu::item {{
                padding: 8px 30px 8px 20px;
                color: {cls.COLORS['text_primary']};
            }}
            
            QMenu::item:selected {{
                background-color: {cls.COLORS['primary_light']};
            }}
            
            QMenu::separator {{
                height: 1px;
                background: {cls.COLORS['border']};
                margin: 5px 10px;
            }}
            
            /* Tool Bar */
            QToolBar {{
                background-color: {cls.COLORS['background_light']};
                border-bottom: 1px solid {cls.COLORS['border']};
                padding: 5px;
                spacing: 5px;
            }}
            
            QToolBar QToolButton {{
                background-color: transparent;
                border: 1px solid transparent;
                border-radius: 4px;
                padding: 8px 12px;
                color: {cls.COLORS['text_primary']};
            }}
            
            QToolBar QToolButton:hover {{
                background-color: {cls.COLORS['primary_light']};
                border: 1px solid {cls.COLORS['primary']};
            }}
            
            QToolBar QToolButton:pressed {{
                background-color: {cls.COLORS['primary']};
                color: {cls.COLORS['background']};
            }}
            
            /* Status Bar */
            QStatusBar {{
                background-color: {cls.COLORS['background_light']};
                border-top: 1px solid {cls.COLORS['border']};
                color: {cls.COLORS['text_secondary']};
            }}
            
            /* Push Buttons */
            QPushButton {{
                background-color: {cls.COLORS['primary']};
                color: {cls.COLORS['background']};
                border: none;
                border-radius: 4px;
                padding: 10px 20px;
                font-weight: bold;
                font-size: 13px;
            }}
            
            QPushButton:hover {{
                background-color: {cls.COLORS['primary_dark']};
            }}
            
            QPushButton:pressed {{
                background-color: {cls.COLORS['primary_dark']};
                padding-top: 11px;
                padding-left: 21px;
            }}
            
            QPushButton:disabled {{
                background-color: {cls.COLORS['background_dark']};
                color: {cls.COLORS['text_disabled']};
            }}
            
            /* Secondary button style */
            QPushButton#clearButton {{
                background-color: {cls.COLORS['background']};
                color: {cls.COLORS['text_primary']};
                border: 1px solid {cls.COLORS['border_dark']};
            }}
            
            QPushButton#clearButton:hover {{
                background-color: {cls.COLORS['background_dark']};
            }}
            
            /* Splitter */
            QSplitter::handle {{
                background-color: {cls.COLORS['border']};
            }}
            
            QSplitter::handle:horizontal {{
                width: 2px;
            }}
            
            QSplitter::handle:vertical {{
                height: 2px;
            }}
            
            QSplitter::handle:hover {{
                background-color: {cls.COLORS['primary']};
            }}
            
            /* List Widget */
            QListWidget {{
                background-color: {cls.COLORS['background']};
                border: 1px solid {cls.COLORS['border']};
                border-radius: 4px;
                padding: 5px;
                alternate-background-color: {cls.COLORS['background_light']};
            }}
            
            QListWidget::item {{
                padding: 8px;
                border-radius: 4px;
            }}
            
            QListWidget::item:selected {{
                background-color: {cls.COLORS['primary_light']};
                color: {cls.COLORS['text_primary']};
            }}
            
            QListWidget::item:hover {{
                background-color: {cls.COLORS['primary_light']};
            }}
            
            /* Text Edit */
            QTextEdit {{
                background-color: {cls.COLORS['background']};
                border: 1px solid {cls.COLORS['border']};
                border-radius: 4px;
                padding: 10px;
                color: {cls.COLORS['text_primary']};
                selection-background-color: {cls.COLORS['primary_light']};
            }}
            
            QTextEdit:focus {{
                border: 1px solid {cls.COLORS['primary']};
            }}
            
            /* Tab Widget */
            QTabWidget::pane {{
                border: 1px solid {cls.COLORS['border']};
                border-radius: 4px;
                background-color: {cls.COLORS['background']};
            }}
            
            QTabBar::tab {{
                background-color: {cls.COLORS['background_light']};
                border: 1px solid {cls.COLORS['border']};
                border-bottom-color: {cls.COLORS['border']};
                border-top-left-radius: 4px;
                border-top-right-radius: 4px;
                padding: 8px 20px;
                margin-right: 2px;
                color: {cls.COLORS['text_secondary']};
            }}
            
            QTabBar::tab:selected {{
                background-color: {cls.COLORS['background']};
                border-bottom-color: {cls.COLORS['background']};
                color: {cls.COLORS['text_primary']};
                font-weight: bold;
            }}
            
            QTabBar::tab:hover {{
                background-color: {cls.COLORS['primary_light']};
            }}
            
            QTabBar::tab:close-button {{
                image: url(close.png);
                subcontrol-position: right;
            }}
            
            /* Scroll Bars */
            QScrollBar:vertical {{
                background-color: {cls.COLORS['background_light']};
                width: 12px;
                border-radius: 6px;
            }}
            
            QScrollBar::handle:vertical {{
                background-color: {cls.COLORS['border_dark']};
                border-radius: 6px;
                min-height: 20px;
            }}
            
            QScrollBar::handle:vertical:hover {{
                background-color: {cls.COLORS['primary']};
            }}
            
            QScrollBar::add-line:vertical,
            QScrollBar::sub-line:vertical {{
                height: 0px;
            }}
            
            QScrollBar:horizontal {{
                background-color: {cls.COLORS['background_light']};
                height: 12px;
                border-radius: 6px;
            }}
            
            QScrollBar::handle:horizontal {{
                background-color: {cls.COLORS['border_dark']};
                border-radius: 6px;
                min-width: 20px;
            }}
            
            QScrollBar::handle:horizontal:hover {{
                background-color: {cls.COLORS['primary']};
            }}
            
            QScrollBar::add-line:horizontal,
            QScrollBar::sub-line:horizontal {{
                width: 0px;
            }}
            
            /* Labels */
            QLabel {{
                color: {cls.COLORS['text_primary']};
            }}
            
            /* Group Box */
            QGroupBox {{
                border: 1px solid {cls.COLORS['border']};
                border-radius: 4px;
                margin-top: 20px;
                padding-top: 15px;
                font-weight: bold;
            }}
            
            QGroupBox::title {{
                subcontrol-origin: margin;
                subcontrol-position: top left;
                padding: 0 5px;
                color: {cls.COLORS['primary']};
            }}
            
            /* Progress Bar */
            QProgressBar {{
                border: 1px solid {cls.COLORS['border']};
                border-radius: 4px;
                text-align: center;
                height: 20px;
                background-color: {cls.COLORS['background_light']};
            }}
            
            QProgressBar::chunk {{
                background-color: {cls.COLORS['primary']};
                border-radius: 3px;
            }}
        '''
    
    @classmethod
    def get_button_style(cls, variant: str = 'primary') -> str:
        """
        Get stylesheet for a button variant.
        
        Args:
            variant: Button variant ('primary', 'secondary', 'success', 'warning', 'error')
        
        Returns:
            str: Qt stylesheet for the button
        """
        colors = {
            'primary': (cls.COLORS['primary'], cls.COLORS['primary_dark']),
            'secondary': (cls.COLORS['background'], cls.COLORS['background_dark']),
            'success': (cls.COLORS['success'], '#388E3C'),
            'warning': (cls.COLORS['warning'], '#F57C00'),
            'error': (cls.COLORS['error'], '#D32F2F'),
        }
        
        bg, bg_dark = colors.get(variant, colors['primary'])
        text_color = cls.COLORS['background'] if variant != 'secondary' else cls.COLORS['text_primary']
        border = f'1px solid {cls.COLORS["border_dark"]}' if variant == 'secondary' else 'none'
        
        return f'''
            QPushButton {{
                background-color: {bg};
                color: {text_color};
                border: {border};
                border-radius: 4px;
                padding: 10px 20px;
                font-weight: bold;
            }}
            
            QPushButton:hover {{
                background-color: {bg_dark};
            }}
            
            QPushButton:pressed {{
                padding-top: 11px;
                padding-left: 21px;
            }}
        '''
