from win10toast import ToastNotifier

toast = ToastNotifier() 

toast.show_toast(
    "Notification",
    "Notification body",
    duration = 20,
    icon_path = "icon.ico",
    threaded = True,
)