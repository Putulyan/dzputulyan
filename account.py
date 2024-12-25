"""
реализовать класс Account, который отражает абстракцию базового
поведения банковского аккаунта:
● создать банковский аккаунт с параметрами: имя; стартовый баланс с
которым зарегистрирован аккаунт; история операций*;
● реализовать два метода, которые позволяют положить деньги на счёт
или снять деньги со счёта;
● продумать, как можно хранить историю поступления или снятия
денег, чтобы с ней было удобно работать*.
"""

import decimal
from datetime import datetime
from enum import StrEnum
import locale


class Logger:
    """
    Базовый класс логирования содержащий только дату и наименование операции
    """

    def __init__(self, operation: str, date: datetime = None, code: StrEnum = None):
        self.__operation = operation
        self.__date = date if date is not None else datetime.now()
        self.__code = code if code is not None else operation

    def __repr__(self):
        return f"{self.__class__.__name__}(operation={self.operation!r}, date={self.date!r}, code={self.code!r})"

    def __str__(self):
        return f"{self.date_formatted} - [{self.operation}]"

    def _key(self):
        return self.date, self.operation, self.code

    def __hash__(self):
        return hash(self._key())

    def __eq__(self, other):
        if isinstance(other, Logger):
            return self._key() == other._key()
        return False

    def __lt__(self, other):
        if isinstance(other, Logger):
            return self.date < other.date
        return False

    def __le__(self, other):
        if isinstance(other, Logger):
            return self.date <= other.date
        return False

    def __gt__(self, other):
        if isinstance(other, Logger):
            return self.date > other.date
        return False

    def __ge__(self, other):
        if isinstance(other, Logger):
            return self.date >= other.date
        return False

    @property
    def date(self) -> datetime:
        """
        Дата операции
        """
        return self.__date

    @property
    def operation(self) -> str:
        """
        Наименование операции
        """
        return self.__operation

    @property
    def code(self) -> StrEnum:
        """
        Код операции
        """
        return self.__code

    @property
    def date_formatted(self) -> str:
        """
        Дата операции в форматированном виде
        """
        return datetime.strftime(self.date, "%d.%m.%Y %H:%M:%S.%f")


class AccountOperationCode(StrEnum):
    """
    Коды событий операций по счету
    """
    ERROR_CODE: str = "ERR"
    CREATE_ACCOUNT_CODE: str = "CRA"
    GET_BALANCE_CODE: str = "GB"
    WITHDRAW_BALANCE_CODE: str = "WDB"
    DEPOSIT_BALANCE_CODE: str = "DPB"


class AccountLogger(Logger):
    """
    Класс логирования для операций с банковским аккаунтом
    """

    def __init__(self, code: AccountOperationCode, operation: str, amount: decimal, balance: decimal):
        super().__init__(operation, code=code)
        self.__amount: decimal = amount
        self.__balance: decimal = balance

    def __repr__(self):
        return f"{self.__class__.__name__}(code={self.code!r}, operation={self.operation!r}, amount={self.amount!r}, balance={self.balance!r})"

    def __str__(self):
        add_info = ""
        if self.amount is not None:
            add_info += f" сумма: {locale.currency(self.amount)}"
        if self.balance is not None:
            if len(add_info):
                add_info += ","
            add_info += f" баланс: {locale.currency(self.balance)}"
        return f"{super().__str__()}{add_info}"

    def __key(self):
        return super()._key(), self.amount, self.balance

    def __hash__(self):
        return hash(self.__key())

    def __eq__(self, other):
        if isinstance(other, AccountLogger):
            return self.__key() == other.__key()
        return False

    @property
    def amount(self) -> decimal:
        """
        Сумма зачисления/снятия
        """
        return self.__amount

    @property
    def balance(self) -> decimal:
        """
        Баланс счета после выполнения операции
        """
        return self.__balance

    @classmethod
    def error_log(cls, operation: str):
        return AccountLogger(AccountOperationCode.ERROR_CODE, operation, amount=None, balance=None)


class Account:
    """
    Класс счета, отражающий базовое поведение банковского аккаунта
    """

    def __init__(self, name: str, balance: decimal, culture: str = "ru_RU"):
        self.name: str = name
        self.__balance: decimal = balance
        self.__history: list[AccountLogger] = []

        locale.setlocale(locale.LC_ALL, culture)
        self.__log(AccountOperationCode.CREATE_ACCOUNT_CODE, "Создание счета")

    def __repr__(self):
        return f"{self.__class__.__name__}(name={self.name!r}, balance={self.__balance!r})"

    def __str__(self):
        return f"Счёт '{self.name}', баланс: {locale.currency(self.__balance)}"

    @property
    def balance(self) -> decimal:
        """
        Баланс по счету
        """
        self.__log(AccountOperationCode.GET_BALANCE_CODE, "Запрос баланса")
        return self.__balance

    def withdraw(self, amount: decimal, show_log: bool = False) -> decimal:
        """
        Снять деньги со счета
        :param amount: сумма для снятия со счета
        :param show_log: показать лог по операции
        :return: текущий баланс по счету
        """
        if amount == 0:
            error = AccountLogger.error_log(f"Запрашиваемая сумма не указана!")
            raise ValueError(str(error))
        elif amount < 0:
            error = AccountLogger.error_log(f"Запрошена отрицательная сумма средств! (сумма: {amount})")
            raise ValueError(str(error))
        elif amount > self.__balance:
            error = AccountLogger.error_log(
                f"Недостаточно средств на счете! (запрошено средств: {locale.currency(amount)})")
            raise ValueError(str(error))
        self.__balance -= amount
        self.__log(AccountOperationCode.WITHDRAW_BALANCE_CODE, "Вывод средств со счёта", -amount, show_log)
        return self.__balance

    def deposit(self, amount: decimal, show_log: bool = False) -> decimal:
        """
        Зачислить деньги на счет
        :param amount: сумма для внесения на счет
        :param show_log: показать лог по операции
        :return: текущий баланс по счету
        """
        if amount == 0:
            error = AccountLogger.error_log(f"Запрашиваемая сумма не указана!")
            raise ValueError(str(error))
        elif amount < 0:
            error = AccountLogger.error_log(f"Указана некорректная сумма для зачисления на счет! (сумма: {amount})")
            raise ValueError(str(error))
        self.__balance += amount
        self.__log(AccountOperationCode.DEPOSIT_BALANCE_CODE, "Зачисление средств на счёт", amount, show_log)
        return self.__balance

    def __log(self, code: AccountOperationCode, operation: str, amount: decimal = None, show_log: bool = False) -> AccountLogger:
        """
        Добавить запись с логом выполнения операции в историю операций со счетом
        :param code: код операции
        :param operation: тип операции
        :param amount: сумма средств по операции
        :param show_log: показать лог по операции
        :return: добавленный в историю объект лога
        """
        log = AccountLogger(code, operation, amount, self.__balance)
        self.__history.append(log)
        if show_log:
            print(log)
        return log

    def show_history(self, operation_code: AccountOperationCode = None, date: tuple[datetime, str] = None) -> None:
        """
        Внести историю операций по счету
        :param operation_code: фильтр по коду операции
        :param date: фильтр по дате (кортеж с датой и знаком сравнения) (<dateime>, <"<=">)
        :return: отфильтрованный список операций
        """
        for log in self.__history:
            if operation_code is not None and log.code != operation_code:
                continue
            if date is not None:
                dt, sign = date
                if ((sign == '>' and log.date <= dt) or
                    (sign == '>=' and log.date < dt) or
                    (sign == '<' and log.date >= dt) or
                    (sign == '<=' and log.date > dt)):
                    continue
            print(log)


def account_operations() -> None:
    """
    Выполнение операций с банковским аккаунтом
    """
    account: Account = None
    while True:
        try:
            if account is not None:
                print()
            operation = input("type operation: ").upper()
            if operation == "?":
                print("""Account commands:
                CRA - create account
                DPB - add money
                WDB - get money
                HST - show all history
                FLT - show history by code
                BLN - show balance
                ACC - account info
                Q - quit program
                ? - help
                """)
            elif operation == "CRA":
                name = input("account name: ")
                balance = decimal.Decimal(input("balance: "))
                account = Account(name, balance)
                print(account)
            elif operation == "DPB":
                if account is not None:
                    amount = decimal.Decimal(input("amount: "))
                    account.deposit(amount, True)
            elif operation == "WDB":
                if account is not None:
                    amount = decimal.Decimal(input("amount: "))
                    account.withdraw(amount, True)
            elif operation == "HST":
                if account is not None:
                    account.show_history()
            elif operation == "FLT":
                if account is not None:
                    operation_code = input("operation code: ")
                    date = input("date: ")
                    if date: sign = input("date comparer sign (>, >=, <, <=): ")
                    account.show_history(operation_code=(AccountOperationCode(operation_code.upper()) if operation_code else None),
                                         date=((datetime.strptime(date, "%d.%m.%Y %H:%M:%S"), sign) if date else None))
            elif operation == "BLN":
                if account is not None:
                    print(f"account balance: {locale.currency(account.balance)}")
            elif operation == "ACC":
                if account is not None:
                    print(account)
            elif operation == "Q":
                break
        except Exception as e:
            print(f"ОШИБКА: {e}")


account_operations()
