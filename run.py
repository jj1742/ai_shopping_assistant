from model import analize, upload_models
from aiogram import Bot, Dispatcher, F, Router
from aiogram.types import CallbackQuery, Message, ContentType
from aiogram import F
from aiogram.filters import CommandStart
from json import load
from gc import collect
from random import shuffle
import asyncio
import logging
import bs4
from requests import get

import keyboards as kb

from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import StatesGroup, State


bot = Bot(token="7909406920:AAHcqnt46obnjsp3THqsZZdFiJsXPviB2SQ")
dp = Dispatcher()

router = Router()
    
models_tup = upload_models()
face_m = models_tup[0]
age_m = models_tup[1]
gen_m = models_tup[2]

catalog = None
with open('catalog.json', 'r') as ctlg:
    catalog = load(ctlg)
    
def set_value(url: str) -> str:
    parser = bs4.BeautifulSoup(get(url).text, 'html.parser')
    
    try:
        for span in parser.find_all('span'):
            if '₽' in span.contents[0]:
                return span.contents[0]
    except Exception as exp:
        print(exp)
        return 'Not found'

@router.message(CommandStart())
async def cmd_start(message=Message):
    
    await message.reply(
        f"Здравствуйте, {message.from_user.first_name}. Я ваш шоппинг ассистент.",
        reply_markup=kb.main,
    )


class Main(StatesGroup):
    choosen = State()
    choosen_person = State()


@router.message(F.text == "Новый запрос")
async def cmd_request(message: Message, state: FSMContext):
    await message.answer(
        "Пришлите картинку. По желанию укажите пол, возраст и ценовой полоток.\nПример:\n- пол: женский, возраст: 16, 2000"
    )
    await state.set_state(Main.choosen)


@router.message(Main.choosen)
async def text_chosing(message: Message, state: FSMContext):
    gender = None
    age = ''
    price_floor = ''
    if message.caption:
        isFound = False
        text = message.caption.lower()

        if "муж" in text:
            gender = "Male"
        elif "жен" in text:
            gender = "Female"
            
        try:
            for word in text:
                if isFound == True and word == ' ':
                    break                 
                if word.isdigit() == True:
                    isFound = True
                    age = age + word
                   
            for word in text[::-1]:
                if word.isdigit() == True:
                    price_floor = price_floor + word
                else:
                    break 
                
            if len(text.split()) == 1 and 'возраст' not in text:
                age = ''
            if len(text.split()) == 1 and 'возраст' in text:
                price_floor = ''           
            if len(text.split()) == 2 and 'возраст' not in text:
                price_floor = ''
                        
            if age != '':
                age = int(age)
            if price_floor != '':
                price_floor = int(price_floor[::-1])
                    
                
            print(f'G: {gender} A: {age} PF: {price_floor}')
                
        except:
            await message.answer("Измените промт.")
            
    try:
        if message.photo[-1].file_id:
            await message.bot.download(
                file=message.photo[-1].file_id, destination="last.jpg"
            )
            await message.answer("Запрос обрабатывается...")
            res = analize("last.jpg", face_m, age_m, gen_m)
            if len(res) > 1:
                await message.answer(
                    "Пришлите номер нужного человека на фото (считая слева)."
                )
                await state.update_data(choosen=(res, age, gender, price_floor))
                await state.set_state(Main.choosen_person)
            elif len(res) == 0:
                await message.answer("Ошибка: люди на фото не обнаружены.")
            else:
                res = res[0]

                if age != '':
                    res[1] = (age - 4, age + 4)
                if gender != None:
                    res[0] = gender

                goal_list = []
                saver = []
                print(res[0])
                gen_ctlg = catalog[res[0]]
                shuffle(gen_ctlg)
                for case in gen_ctlg:
                    if len(goal_list) < 10:
                        if (res[1][0] <= case[1][1] and case[1][0] <= res[1][1]) and (((case[2][0] in range(res[2][0] - 40, res[2][0] + 40)) and (case[2][1] in range(res[2][1] - 40, res[2][1] + 40)) and (case[2][2] in range(res[2][2] - 40, res[2][2] + 40))) or ((case[2][0] in range(255 - res[2][0] - 40, 255 - res[2][0] + 40)) and (case[2][1] in range(255 - res[2][1] - 40, 255 - res[2][1] + 40)) and (case[2][2] in range(255 - res[2][2] - 40, 255 - res[2][2] + 40)))):
                            if price_floor != '':
                                if int(str(set_value(case[0]))[:-2].replace(' ', '')) < price_floor:
                                    goal_list.append((case[0], set_value(case[0])))
                            else:
                                goal_list.append((case[0], set_value(case[0])))
                        elif res[1][0] <= case[1][1] and case[1][0] <= res[1][1]:
                            if len(saver) < 10:
                                if price_floor != '':
                                    if int(str(set_value(case[0]))[:-2].replace(' ', '')) < price_floor:
                                        saver.append((case[0], set_value(case[0])))
                                else:
                                    saver.append((case[0], set_value(case[0])))
                        goal_list = list(set(goal_list))
                    else:
                        break
                    
                answer = ''
                
                if len(goal_list) < 10:
                    i = 0
                    while len(goal_list) < 10:
                        if saver[i] not in goal_list:
                            goal_list.append(saver[i])
                        i = i + 1
                        if i == len(saver):
                            break
                
                del gen_ctlg, saver
                collect()
                
                if len(goal_list) == 0:
                    answer == 'Not Found'
                else:
                    ind = 1
                    for case in goal_list: 
                        answer = answer + f'{ind}. {case[0]} ({case[1]})\n'
                        ind = ind + 1
                
                await message.answer(answer)
                await state.clear()

        else:
            await message.answer("Пришлите фотографию с человеком (людьми).")
    except TypeError as te:
        await message.answer(f"Пришлите сжатое фото.")
        print(te)
        
    except Exception as ex:
        await message.answer(f"Пришлите другое фото или измените промт.")
        print(ex)


@router.message(Main.choosen_person)
async def person_chosen(message: Message, state: FSMContext):
    data = await state.get_data()
    age = data["choosen"][1]
    gender = data["choosen"][2]
    res = data["choosen"][0]
    price_floor = data["choosen"][3]
    try:
        person = int(message.text)
    except:
        await message.answer(f"Повторите запрос (номер человека обозначается числом)")
        return None
    try:
        res = res[person - 1]
    except:
        res = res[-1]
    if age != "":
        res[1] = (age - 3, age + 3)
    if gender != None:
        res[0] = gender

    try:
        goal_list = []
        saver = []
        print(res[0])
        gen_ctlg = catalog[res[0]]
        shuffle(gen_ctlg)
        for case in gen_ctlg:
            if len(goal_list) < 10:
                if (res[1][0] <= case[1][1] and case[1][0] <= res[1][1]) and (((case[2][0] in range(res[2][0] - 40, res[2][0] + 40)) and (case[2][1] in range(res[2][1] - 40, res[2][1] + 40)) and (case[2][2] in range(res[2][2] - 40, res[2][2] + 40))) or ((case[2][0] in range(255 - res[2][0] - 40, 255 - res[2][0] + 40)) and (case[2][1] in range(255 - res[2][1] - 40, 255 - res[2][1] + 40)) and (case[2][2] in range(255 - res[2][2] - 40, 255 - res[2][2] + 40)))):
                    if price_floor != '':
                        if int(str(set_value(case[0]))[:-2].replace(' ', '')) < price_floor:
                            goal_list.append((case[0], set_value(case[0])))
                    else:
                        goal_list.append((case[0], set_value(case[0])))
                elif res[1][0] <= case[1][1] and case[1][0] <= res[1][1]:
                    if len(saver) < 10:
                        if price_floor != '':
                            if int(str(set_value(case[0]))[:-2].replace(' ', '')) < price_floor:
                                saver.append((case[0], set_value(case[0])))
                        else:
                            saver.append((case[0], set_value(case[0])))
                goal_list = list(set(goal_list))
            else:
                break
                        
        answer = ''
                    
        if len(goal_list) < 10:
            i = 0
            while len(goal_list) < 10:
                if saver[i] not in goal_list:
                    goal_list.append(saver[i])
                i = i + 1
                if i == len(saver):
                    break
                    
        del gen_ctlg, saver
        collect()
                    
        if len(goal_list) == 0:
            answer == 'Not Found'
        else:
            ind = 1
            for case in goal_list: 
                answer = answer + f'{ind}. {case[0]} ({case[1]})\n'
                ind = ind + 1
                    
        await message.answer(answer)
    except:
        await message.answer(f"Пришлите другое фото или измените промт.")
    await state.clear()


async def main():
    dp.include_router(router)
    await dp.start_polling(bot)


if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        print("Exit")
