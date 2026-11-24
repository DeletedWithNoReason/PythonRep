import random
import threading
import time
from dataclasses import dataclass, field


@dataclass
class Warehouse:
    name: str
    meds: int
    price_per_unit: float
    use_lock: bool = True
    lock: threading.Lock = field(default_factory=threading.Lock, repr=False)
    initial_meds: int = field(init=False)
    stolen_meds: int = field(default=0, init=False)
    lost_meds: int = field(default=0, init=False)
    earned: float = field(default=0.0, init=False)

    def __post_init__(self):
        self.initial_meds = self.meds

    def _maybe_acquire(self):
        if self.use_lock:
            self.lock.acquire()

    def _maybe_release(self):
        if self.use_lock and self.lock.locked():
            self.lock.release()

    def steal(self, amount: int) -> tuple[int, float, str]:
        self._maybe_acquire()
        try:
            outcome = random.choice(["success", "lost", "caught"])

            if outcome == "caught":
                return 0, 0.0, "спіймали"

            if outcome == "lost":
                lost_amount = random.randint(1, max(1, amount))
                current_meds = self.meds

                if not self.use_lock:
                    time.sleep(0.001)

                actual_lost = min(current_meds, lost_amount)
                self.meds = current_meds - actual_lost
                self.lost_meds += actual_lost
                return 0, 0.0, f"втрачено ({actual_lost})"

            current_meds = self.meds

            if not self.use_lock:
                time.sleep(0.001)

            actual_stolen = min(current_meds, amount)
            self.meds = current_meds - actual_stolen
            self.stolen_meds += actual_stolen
            profit = actual_stolen * self.price_per_unit
            self.earned += profit
            return actual_stolen, profit, f"успіх (+{actual_stolen})"
        finally:
            self._maybe_release()


class Runner(threading.Thread):
    def __init__(self, warehouse: Warehouse, thief_name: str, attempts: int = 10, show_progress: bool = True):
        super().__init__(name=thief_name)
        self.warehouse = warehouse
        self.thief_name = thief_name
        self.attempts = attempts
        self.show_progress = show_progress
        self.total_stolen = 0
        self.total_earned = 0.0
        self.progress = 0

    def _render_bar(self, status: str):
        bar_len = 10
        filled = int(bar_len * self.progress / self.attempts)
        bar = "█" * filled + "░" * (bar_len - filled)
        print(f"  [{self.thief_name:10s} -> {self.warehouse.name:10s}] |{bar}| {self.progress:2d}/{self.attempts} ({status})")

    def run(self):
        for _ in range(self.attempts):
            amount = random.randint(10, 30)
            stolen, profit, status = self.warehouse.steal(amount)
            self.total_stolen += stolen
            self.total_earned += profit
            self.progress += 1

            if self.show_progress:
                self._render_bar(status)

            time.sleep(random.uniform(0.1, 0.5))


def check_invariants(warehouses: list[Warehouse], runners: list[Runner]):
    for w in warehouses:
        assert w.meds >= 0, f"Інваріант 1 порушено: на складі '{w.name}' meds = {w.meds} (< 0)"

    for w in warehouses:
        total_removed = w.stolen_meds + w.lost_meds
        assert w.initial_meds == w.meds + total_removed, (
            f"Інваріант 2 порушено на складі '{w.name}': "
            f"було={w.initial_meds}, залишилось={w.meds}, вкрадено={w.stolen_meds}, втрачено={w.lost_meds}"
        )

    expected_total_profit = sum(w.stolen_meds * w.price_per_unit for w in warehouses)
    actual_total_profit = sum(r.total_earned for r in runners)
    assert abs(expected_total_profit - actual_total_profit) < 1e-6, (
        f"Інваріант 3 порушено: очікуваний прибуток={expected_total_profit:.2f}, "
        f"фактичний={actual_total_profit:.2f}"
    )


def run_simulation(use_lock: bool = True, show_progress: bool = True, sleep_between_attempts: bool = True):
    warehouses = [
        Warehouse("Склад-А", random.randint(100, 300), price_per_unit=15.0, use_lock=use_lock),
        Warehouse("Склад-Б", random.randint(100, 300), price_per_unit=25.0, use_lock=use_lock),
        Warehouse("Склад-В", random.randint(100, 300), price_per_unit=40.0, use_lock=use_lock),
    ]

    thief_names = ["Шустрий", "Тінь", "Фантом", "Іскра", "Ворон"]
    runners = []
    for idx, name in enumerate(thief_names):
        target_warehouse = warehouses[idx % len(warehouses)]
        runner = Runner(target_warehouse, name, attempts=10, show_progress=show_progress)
        if not sleep_between_attempts:
            runner.run = lambda r=runner: _fast_runner_run(r)
        runners.append(runner)

    for r in runners:
        r.start()

    for r in runners:
        r.join()

    total_earned = sum(r.total_earned for r in runners)
    return warehouses, runners, total_earned


def _fast_runner_run(runner: Runner):
    for _ in range(runner.attempts):
        amount = random.randint(10, 30)
        stolen, profit, _ = runner.warehouse.steal(amount)
        runner.total_stolen += stolen
        runner.total_earned += profit
        runner.progress += 1


def print_report(warehouses: list[Warehouse], total_earned: float):
    print("\n--- ЗВІТ ПО СКЛАДАХ ---")
    for w in warehouses:
        print(
            f"  {w.name}: було={w.initial_meds}, залишилось={w.meds}, "
            f"вкрадено={w.stolen_meds}, втрачено={w.lost_meds}, ціна/од={w.price_per_unit:.2f}"
        )
    print(f"Загалом «заробили» бігуни: {total_earned:.2f}\n")


if __name__ == "__main__":
    print("=== 1. Демонстраційний прогін із прогрес-баром (lock увімкнено) ===")
    wh, rn, earned = run_simulation(use_lock=True, show_progress=True, sleep_between_attempts=True)
    check_invariants(wh, rn)
    print_report(wh, earned)

    print("=== 2. Перевірка інваріантів на 100 прогонах (lock увімкнено) ===")
    for run_idx in range(1, 101):
        wh, rn, earned = run_simulation(use_lock=True, show_progress=False, sleep_between_attempts=False)
        check_invariants(wh, rn)
    print("Усі 100 прогонів із lock пройшли без порушення інваріантів!\n")

    print("=== 3. Тест без lock + пауза time.sleep(0.001) між перевіркою та списанням ===")
    broken_run = None
    broken_error = None
    for run_idx in range(1, 201):
        wh, rn, earned = run_simulation(use_lock=False, show_progress=False, sleep_between_attempts=False)
        try:
            check_invariants(wh, rn)
        except AssertionError as err:
            broken_run = run_idx
            broken_error = str(err)
            break

    if broken_run is not None:
        print(f"Зламалось на прогоні #{broken_run}!")
        print(f"Причина: {broken_error}")
    else:
        print("За 200 прогонів гонка не встигла зламати assert (можна збільшити кількість ітерацій).")