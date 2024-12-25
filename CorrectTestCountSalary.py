def test_calculate_monthly_salary():
    """
    Тесты для функции calculate_monthly_salary.
    """
    from CountSalary import calculate_monthly_salary

    # Тест 1: Зарплата 100 000 ниже порога 2.4 млн (ставка 13%)
    monthly_salary = 100_000  # Месячная зарплата
    _, total_gross, total_net = calculate_monthly_salary(monthly_salary)
    expected_gross = 100_000 * 12  # Доход до налогообложения
    expected_net = expected_gross * (1 - 0.13)  # Учитываем ставку 13%
    assert total_gross == expected_gross, f"Ошибка: {total_gross} != {expected_gross}"
    assert round(total_net, 2) == round(expected_net, 2), f"Ошибка: {total_net} != {expected_net}"

    print("Все тесты пройдены успешно!")


# Запуск тестов
test_calculate_monthly_salary()