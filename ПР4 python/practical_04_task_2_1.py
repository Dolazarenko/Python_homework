# practical_04_task_2_1.py

"""Демонстрація race condition та захист через Lock."""

import threading
import time
import random


class BankAccount:
    """Банківський рахунок без синхронізації (небезпечний)."""

    def __init__(self, balance: float = 0.0):
        self.balance = balance
        self.transaction_count = 0

    def deposit(self, amount: float) -> None:
        """Поповнення рахунку."""
        # Імітація неатомарної операції
        current = self.balance
        time.sleep(random.uniform(0.0001, 0.001))
        self.balance = current + amount
        self.transaction_count += 1

    def withdraw(self, amount: float) -> bool:
        """Зняття коштів. Повертає True, якщо операція успішна."""
        current = self.balance
        time.sleep(random.uniform(0.0001, 0.001))
        if current >= amount:
            self.balance = current - amount
            self.transaction_count += 1
            return True
        return False


class SafeBankAccount:
    """Банківський рахунок із синхронізацією через Lock."""

    def __init__(self, balance: float = 0.0):
        self.balance = balance
        self.transaction_count = 0
        self._lock = threading.Lock()

    def deposit(self, amount: float) -> None:
        with self._lock:
            current = self.balance
            time.sleep(random.uniform(0.0001, 0.001))
            self.balance = current + amount
            self.transaction_count += 1

    def withdraw(self, amount: float) -> bool:
        with self._lock:
            current = self.balance
            time.sleep(random.uniform(0.0001, 0.001))
            if current >= amount:
                self.balance = current - amount
                self.transaction_count += 1
                return True
            return False


def run_transactions(account, num_deposits: int, num_withdrawals: int,
                     deposit_amount: float = 50.0, withdraw_amount: float = 50.0,
                     num_threads: int = 10) -> None:
    """Запускає num_threads потоків поповнення та num_threads потоків зняття.

    Загальна кількість операцій ділиться порівну між потоками.
    """
    dep_per_thread = num_deposits // num_threads
    wd_per_thread = num_withdrawals // num_threads

    def deposit_worker():
        for _ in range(dep_per_thread):
            account.deposit(deposit_amount)

    def withdraw_worker():
        for _ in range(wd_per_thread):
            # Якщо коштів тимчасово бракує — повторюємо спробу,
            # щоб загальна кількість успішних зняттів була очікуваною
            for _attempt in range(1000):
                if account.withdraw(withdraw_amount):
                    break
                time.sleep(0.001)

    threads = (
        [threading.Thread(target=deposit_worker, name=f"Dep-{i}") for i in range(num_threads)]
        + [threading.Thread(target=withdraw_worker, name=f"Wd-{i}") for i in range(num_threads)]
    )
    for t in threads:
        t.start()
    for t in threads:
        t.join()


def main():
    initial_balance = 1000.0
    num_deposits = 100
    deposit_amount = 50.0
    num_withdrawals = 100
    withdraw_amount = 50.0

    expected_balance = (
        initial_balance
        + num_deposits * deposit_amount
        - num_withdrawals * withdraw_amount
    )
    expected_transactions = num_deposits + num_withdrawals

    # === Тест 1: Без синхронізації ===
    print("=== Тест без синхронізації ===")
    unsafe_account = BankAccount(initial_balance)
    run_transactions(unsafe_account, num_deposits, num_withdrawals,
                     deposit_amount, withdraw_amount)
    print(f"Очікуваний баланс: {expected_balance:.2f}")
    print(f"Фактичний баланс:  {unsafe_account.balance:.2f}")
    print(f"Транзакцій: {unsafe_account.transaction_count} (очікувано {expected_transactions})")
    print("Збігаються:", unsafe_account.balance == expected_balance,
          "<-- RACE CONDITION!" if unsafe_account.balance != expected_balance else "")

    # === Тест 2: З синхронізацією (Lock) ===
    print("\n=== Тест із синхронізацією (Lock) ===")
    safe_account = SafeBankAccount(initial_balance)
    run_transactions(safe_account, num_deposits, num_withdrawals,
                     deposit_amount, withdraw_amount)
    print(f"Очікуваний баланс: {expected_balance:.2f}")
    print(f"Фактичний баланс:  {safe_account.balance:.2f}")
    print(f"Транзакцій: {safe_account.transaction_count} (очікувано {expected_transactions})")
    ok = safe_account.balance == expected_balance
    print("Збігаються:", ok, "-> коректно" if ok else "-> ПОМИЛКА")

    print(f"\nОчікуваний баланс: {expected_balance:.2f}")


if __name__ == "__main__":
    main()
