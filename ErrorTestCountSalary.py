def test_calculate_monthly_salary():
    """
    Тесты для функции calculate_monthly_salary.
    
    """
    from CountSalary import calculate_monthly_salary
    
    # Тест 2: Зарплата 250 000 выше порога 2.4 млн, но ниже 5 млн (ставка 13% и 15%)
    monthly_salary = 250_000
    _, total_gross, total_net = calculate_monthly_salary(monthly_salary)
    expected_gross = 250_000 * 12
    # Расчет налогов:
    limit_13 = 2_400_000
    limit_15 = expected_gross - 2_400_000
    tax = limit_13 * 0.13 + limit_15 * 0.15
    expected_net = expected_gross - tax
    assert total_gross == expected_gross, f"Ошибка: {total_gross} != {expected_gross}"
    assert round(total_net, 2) == round(expected_net, 2), f"Ошибка: {total_net} != {expected_net}"

    print("Все тесты пройдены успешно!")


# Запуск тестов
test_calculate_monthly_salary()