
class Base:
    class Name:

        seke = 'seke'
        moallem = 'moallem'

    name = Name.moallem

class Constants:
    if Base.name == Base.Name.seke:
        NAME = 'سکه طلا'
        PWA_NAME = 'مدیریت سکه طلا'
        PWA_DESCRIPTION = 'مدیریت انبار و دستیار هوشمند سکه طلا'
        PWA_COLOR = "#FFD900"
        PWA_BACKGROUND_COLOR = '#FFFFFF'
        LOGO_PATH = 'icons/logo.gif'
    
    elif Base.name == Base.Name.moallem:
        NAME = 'خانه معلم'
        PWA_NAME = 'مدیریت خانه معلم'
        PWA_DESCRIPTION = 'مدیریت انبار و دستیار هوشمند خانه معلم'
        PWA_COLOR = "#2723FC"
        PWA_BACKGROUND_COLOR = "#74B0FF"
        LOGO_PATH = 'icons/logo.gif'
