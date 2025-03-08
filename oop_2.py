"""
В этом задании будем улучшать нашу систему классов из задания прошлой лекции
(Student, Teacher, Homework)
Советую обратить внимание на defaultdict из модуля collection для
использования как общую переменную


1. Как то не правильно, что после do_homework мы возвращаем все тот же
объект - будем возвращать какой-то результат работы (HomeworkResult)

HomeworkResult принимает объект автора задания, принимает исходное задание
и его решение в виде строки
Атрибуты:
    homework - для объекта Homework, если передан не этот класс -  выкинуть
    подходящие по смыслу исключение с сообщением:
    'You gave a not Homework object'

    solution - хранит решение ДЗ как строку
    author - хранит объект Student
    created - c точной датой и временем создания

2. Если задание уже просрочено хотелось бы видеть исключение при do_homework,
а не просто принт 'You are late'.
Поднимайте исключение DeadlineError с сообщением 'You are late' вместо print.

3. Student и Teacher имеют одинаковые по смыслу атрибуты
(last_name, first_name) - избавиться от дублирования с помощью наследования

4.
Teacher
Атрибут:
    homework_done - структура с интерфейсом как в словаря, сюда поподают все
    HomeworkResult после успешного прохождения check_homework
    (нужно гарантировать остутствие повторяющихся результатов по каждому
    заданию), группировать по экземплярам Homework.
    Общий для всех учителей. Вариант ипользования смотри в блоке if __main__...
Методы:
    check_homework - принимает экземпляр HomeworkResult и возвращает True если
    ответ студента больше 5 символов, так же при успешной проверке добавить в
    homework_done.
    Если меньше 5 символов - никуда не добавлять и вернуть False.

    reset_results - если передать экземпряр Homework - удаляет только
    результаты этого задания из homework_done, если ничего не передавать,
    то полностью обнулит homework_done.

PEP8 соблюдать строго.
Всем перечисленным выше атрибутам и методам классов сохранить названия.
К названием остальных переменных, классов и тд. подходить ответственно -
давать логичные подходящие имена.
"""


from collections import defaultdict
from datetime import datetime, timedelta

class DeadlineError(Exception):
    pass

class Homework:
    def __init__(self, text, days):
        self.text = text
        self.deadline = timedelta(days=days)
        self.created = datetime.now()

    def is_active(self):
        return datetime.now() < self.created + self.deadline

class Person:
    def __init__(self, last_name, first_name):
        self.last_name = last_name
        self.first_name = first_name

class Student(Person):
    def do_homework(self, homework, solution):
        if not isinstance(homework, Homework):
            raise ValueError('You gave a not Homework object')
        if not homework.is_active():
            raise DeadlineError('You are late')
        return HomeworkResult(self, homework, solution)

class Teacher(Person):
    homework_done = defaultdict(set)

    def create_homework(self, text, days):
        return Homework(text, days)

    def check_homework(self, homework_result):
        if len(homework_result.solution) > 5:
            self.homework_done[homework_result.homework].add(homework_result)
            return True
        return False

    def reset_results(self, homework=None):
        if homework:
            if homework in self.homework_done:
                del self.homework_done[homework]
        else:
            self.homework_done.clear()

class HomeworkResult:
    def __init__(self, author, homework, solution):
        if not isinstance(homework, Homework):
            raise ValueError('You gave a not Homework object')
        self.homework = homework
        self.solution = solution
        self.author = author
        self.created = datetime.now()

if __name__ == '__main__':
    opp_teacher = Teacher('Daniil', 'Shadrin')
    advanced_python_teacher = Teacher('Aleksandr', 'Smetanin')

    lazy_student = Student('Roman', 'Petrov')
    good_student = Student('Lev', 'Sokolov')

    oop_hw = opp_teacher.create_homework('Learn OOP', 1)
    docs_hw = opp_teacher.create_homework('Read docs', 5)

    try:
        result_1 = good_student.do_homework(oop_hw, 'I have done this hw')
        result_2 = good_student.do_homework(docs_hw, 'I have done this hw too')
        result_3 = lazy_student.do_homework(docs_hw, 'done')
    except DeadlineError as e:
        print(e)

    try:
        result_4 = HomeworkResult(good_student, "fff", "Solution")
    except Exception:
        print('There was an exception here')

    opp_teacher.check_homework(result_1)
    temp_1 = opp_teacher.homework_done

    advanced_python_teacher.check_homework(result_1)
    temp_2 = advanced_python_teacher.homework_done
    assert temp_1 == temp_2

    opp_teacher.check_homework(result_2)
    opp_teacher.check_homework(result_3)

    print(opp_teacher.homework_done[oop_hw])
    opp_teacher.reset_results()