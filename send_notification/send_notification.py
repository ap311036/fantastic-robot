from Foundation import NSUserNotification, NSUserNotificationCenter


def send_notification(title, subtitle, info_text):
    notification = NSUserNotification.alloc().init()
    notification.setTitle_(title)
    notification.setSubtitle_(subtitle)
    notification.setInformativeText_(info_text)
    notification.setSoundName_("NSUserNotificationDefaultSoundName")
    NSUserNotificationCenter.defaultUserNotificationCenter().deliverNotification_(
        notification
    )
