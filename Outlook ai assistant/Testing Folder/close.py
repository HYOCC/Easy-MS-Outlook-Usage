import webview

def on_closing():
    window.minimize()
    return False  # Prevents the window from closing

if __name__ == '__main__':
    window = webview.create_window('My App', 'https://pywebview.flowrl.com/hello')
    window.events.closing += on_closing
    webview.start()