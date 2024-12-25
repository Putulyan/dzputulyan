def calculate_monthly_salary(pre_tax_salary):
    """
    Рассчитывает помесячную зарплату до и после налогообложения по прогрессивной шкале.
    
    :param pre_tax_salary: Месячная зарплата до налогообложения.
    :return: Список помесячных доходов (до налогообложения и к выплате) и итоговые суммы.
    """
    # Налоговые лимиты и ставки
    tax_brackets = [
        (2_400_000, 0.13),  # До 2.4 млн руб. в год
        (5_000_000, 0.15),  # От 2.4 до 5 млн руб. в год
        (20_000_000, 0.18), # От 5 до 20 млн руб. в год
        (50_000_000, 0.20), # От 20 до 50 млн руб. в год
        (float('inf'), 0.22)  # Свыше 50 млн руб. в год
    ]
    
    total_income = 0  # Накопленный доход с начала года
    monthly_results = []  # Список для хранения помесячных данных
    
    for month in range(1, 13):
        total_income += pre_tax_salary  # Накопленный доход на текущий месяц
        remaining_income = pre_tax_salary  # Остаток месячного дохода для налогообложения
        monthly_tax = 0  # Налог за текущий месяц
        
        # Применяем налоговые ставки
        cumulative_income = total_income - pre_tax_salary  # Доход до текущего месяца
        for limit, rate in tax_brackets:
            # Определяем, сколько дохода облагается в текущем лимите
            if cumulative_income >= limit:
                continue  # Пропускаем, если лимит уже полностью покрыт
            taxable_income = min(remaining_income, limit - cumulative_income)
            monthly_tax += taxable_income * rate
            cumulative_income += taxable_income
            remaining_income -= taxable_income
            
            if remaining_income <= 0:
                break
        
        post_tax_salary = pre_tax_salary - monthly_tax
        monthly_results.append((pre_tax_salary, round(post_tax_salary, 2)))
    
    total_pre_tax = sum([month[0] for month in monthly_results])
    total_post_tax = sum([month[1] for month in monthly_results])
    
    return monthly_results, total_pre_tax, total_post_tax

# Пример использования
#monthly_salary = 310_345  # Введите месячную зарплату до налогообложения
#results, total_gross, total_net = calculate_monthly_salary(monthly_salary)

# Вывод результатов
#print("Месяц | До налогообложения | К выплате")
#for i, (gross, net) in enumerate(results, start=1):
#    print(f"{i:>5} | {gross:>18,.2f} | {net:>10,.2f}")

# Расчёт потерь при фиксированной ставке 0.13
#fixed_rate_net = total_gross * (1 - 0.13)
#loss_due_to_dynamic_tax = fixed_rate_net - total_net

#print("\nИтоговая зарплата за год:")
#print(f"До налогообложения: {total_gross:,.2f} руб.")
#print(f"К выплате (динамическая ставка): {total_net:,.2f} руб.")
#print(f"К выплате (фиксированная ставка 13%): {fixed_rate_net:,.2f} руб.")
#print(f"Разница из-за динамической ставки: {loss_due_to_dynamic_tax:,.2f} руб.")