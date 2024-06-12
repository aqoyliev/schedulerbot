from loader import db

# import asyncio
# from datetime import datetime
from googletrans import Translator
trans = Translator()


# weekdays
# weekdays = ['monday','tuesday','wednesday','thursday','friday','saturday','sunday']
weekdays = ['Dushanba', 'Seshanba', 'Chorshanba', 'Payshanba', 'Juma', 'Shanba', 'Yakshanba']

async def get_schedules(when='Today', group_id=None, day=None, language='en'):
    # day = weekdays[datetime.now().weekday()]
    try:
        lessons = await db.select_schedules(group_id=group_id, day=day)
        # lessons.sort(key=lambda lesson: lesson[5])
        schedule = f"{trans.translate(when,dest=language).text.capitalize()}:  <b>{trans.translate(day,dest=language).text.capitalize()}</b>\n"
        lessons_list, k = [], 1
        for lesson in lessons:
            science = str(await db.select_science(lesson['id']))
            teacher = str(await db.select_teacher(lesson['id']))
            room = str(await db.select_room(lesson['id']))
            start_time = str(await db.select_start_time(lesson['id']))
            lessons_list.append(
        f"""
{k}. <i>{science}</i>
{trans.translate("O'qituvchi",dest=language).text}:  {teacher}
{trans.translate("Xona",dest=language).text}:  {room}
{trans.translate("Boshlanish vaqti",dest=language).text}:  {start_time}
        """
            )
            k += 1
        schedule += "\n********************\n".join(lessons_list)
        # return schedule if (len(schedule) < 150) else trans.translate("Jadval topilmadi😔",dest=language).text
        return schedule
    except:
        return trans.translate("Jadval topilmadi😔\nBazadan ma'lumotlarni olishda muammo yuzaga keldi.",dest=language).text

# to'liq haftalik dars jadvalni jo'natish
async def get_full_schedules(group_id, day, language):
    try:
        lessons = await db.select_schedules(group_id=group_id, day=day)
        # lessons.sort(key=lambda lesson: db.select_time_name(lesson['time_id']))
        schedule = f"{trans.translate('Day:',dest=language).text.capitalize()}  <b>{trans.translate(day,dest=language).text.capitalize()}</b>\n"
        lessons_list, k = [], 1
        for lesson in lessons:
            science = str(await db.select_science(lesson['id']))
            teacher = str(await db.select_teacher(lesson['id']))
            room = str(await db.select_room(lesson['id']))
            start_time = str(await db.select_start_time(lesson['id']))
            lessons_list.append(
        f"""
{k}. <i>{science}</i>
{trans.translate("O'qituvchi",dest=language).text}:  {teacher}
{trans.translate("Xona",dest=language).text}:  {room}
{trans.translate("Boshlanish vaqti",dest=language).text}:  {start_time}
        """
            )
            k += 1
        schedule += "\n********************\n".join(lessons_list)
        # return schedule if (len(schedule) < 150) else None
        return schedule
    except:
        return trans.translate("Jadval topilmadi😔\nBazadan ma'lumotlarni olishda muammo yuzaga keldi.",dest=language).text


# print(asyncio.run(get_schedule('3e9c1058-baa2-476a-9ab9-1c6d1023c615','uz')))