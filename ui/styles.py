import tkinter as tk
from tkinter import ttk

class ThemeManager:
    """Manejo de temas visuales (Claro y Oscuro) con estilos ttk modernos."""
    
    PALETTES = {
        'light': {
            'bg': '#f4f6f9',
            'fg': '#1e293b',
            'card_bg': '#ffffff',
            'border': '#cbd5e1',
            'primary': '#2563eb',
            'primary_fg': '#ffffff',
            'secondary': '#64748b',
            'accent': '#0d9488',
            'danger': '#dc2626',
            'danger_fg': '#ffffff',
            'success': '#16a34a',
            'tree_bg': '#ffffff',
            'tree_fg': '#1e293b',
            'tree_select_bg': '#2563eb',
            'tree_select_fg': '#ffffff',
            'entry_bg': '#ffffff',
            'entry_fg': '#0f172a'
        },
        'dark': {
            'bg': '#0f172a',
            'fg': '#f8fafc',
            'card_bg': '#1e293b',
            'border': '#334155',
            'primary': '#3b82f6',
            'primary_fg': '#ffffff',
            'secondary': '#94a3b8',
            'accent': '#14b8a6',
            'danger': '#ef4444',
            'danger_fg': '#ffffff',
            'success': '#22c55e',
            'tree_bg': '#1e293b',
            'tree_fg': '#f8fafc',
            'tree_select_bg': '#3b82f6',
            'tree_select_fg': '#ffffff',
            'entry_bg': '#334155',
            'entry_fg': '#f8fafc'
        }
    }

    def __init__(self, root: tk.Tk):
        self.root = root
        self.current_theme = 'light'
        self.style = ttk.Style()
        self.style.theme_use('clam')
        self.apply_theme('light')

    def apply_theme(self, theme_name: str):
        if theme_name not in self.PALETTES:
            theme_name = 'light'
        self.current_theme = theme_name
        colors = self.PALETTES[theme_name]

        self.root.configure(bg=colors['bg'])

        # Configuración de estilos ttk
        self.style.configure('.',
            background=colors['bg'],
            foreground=colors['fg'],
            font=('Segoe UI', 10)
        )

        self.style.configure('TFrame', background=colors['bg'])
        self.style.configure('Card.TFrame', background=colors['card_bg'], relief='flat')

        self.style.configure('TLabel', background=colors['bg'], foreground=colors['fg'])
        self.style.configure('Card.TLabel', background=colors['card_bg'], foreground=colors['fg'])
        self.style.configure('Header.TLabel', font=('Segoe UI', 14, 'bold'), foreground=colors['primary'])
        self.style.configure('Subheader.TLabel', font=('Segoe UI', 11, 'bold'), foreground=colors['fg'])

        self.style.configure('TButton',
            font=('Segoe UI', 9, 'bold'),
            padding=(10, 6),
            background=colors['card_bg'],
            foreground=colors['fg'],
            bordercolor=colors['border']
        )
        self.style.map('TButton',
            background=[('active', colors['border'])],
            foreground=[('active', colors['fg'])]
        )

        self.style.configure('Primary.TButton',
            background=colors['primary'],
            foreground=colors['primary_fg'],
            bordercolor=colors['primary']
        )
        self.style.map('Primary.TButton',
            background=[('active', colors['accent'])]
        )

        self.style.configure('Danger.TButton',
            background=colors['danger'],
            foreground=colors['danger_fg'],
            bordercolor=colors['danger']
        )

        # Treeview
        self.style.configure('Treeview',
            background=colors['tree_bg'],
            foreground=colors['tree_fg'],
            fieldbackground=colors['tree_bg'],
            rowheight=26,
            font=('Segoe UI', 9)
        )
        self.style.map('Treeview',
            background=[('selected', colors['tree_select_bg'])],
            foreground=[('selected', colors['tree_select_fg'])]
        )
        self.style.configure('Treeview.Heading',
            background=colors['card_bg'],
            foreground=colors['fg'],
            font=('Segoe UI', 9, 'bold'),
            padding=(6, 4)
        )

        # Entry & Combobox
        self.style.configure('TEntry', fieldbackground=colors['entry_bg'], foreground=colors['entry_fg'])
        self.style.configure('TCombobox', fieldbackground=colors['entry_bg'], foreground=colors['entry_fg'])

        # Notebook
        self.style.configure('TNotebook', background=colors['bg'], borderwidth=0)
        self.style.configure('TNotebook.Tab',
            padding=(12, 6),
            font=('Segoe UI', 10, 'bold'),
            background=colors['card_bg'],
            foreground=colors['fg']
        )
        self.style.map('TNotebook.Tab',
            background=[('selected', colors['primary'])],
            foreground=[('selected', colors['primary_fg'])]
        )

    def toggle_theme(self):
        new_theme = 'dark' if self.current_theme == 'light' else 'light'
        self.apply_theme(new_theme)
        return new_theme
