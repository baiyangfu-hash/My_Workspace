import webview
import inspect

# Version
try:
    print("pywebview version:", webview.__version__)
except:
    try:
        print("pywebview version:", webview.VERSION)
    except:
        print("pywebview version: unknown")

sig = inspect.signature(webview.create_window)
print("create_window params:", list(sig.parameters.keys()))
sig2 = inspect.signature(webview.start)
print("start params:", list(sig2.parameters.keys()))

# Check Window for events/loaded
print("\nWindow public attrs:")
for attr in sorted(dir(webview.Window)):
    if not attr.startswith('_'):
        print(f"  {attr}")
