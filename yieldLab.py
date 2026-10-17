def transaction_stream():
  yield "payment 120"
  yield "refund 50"
  yield "invalid_row_format"
  yield "transfer 300"
  yield "payment 80"


def shadow(limit=200):
  def decorator(func):
    def wrapper(*args, **kwargs):
      total = 0
      limit_exceeded = False
      for item in func(*args, **kwargs):
        parts = item.split()
        if len(parts) == 2:
          try:
            val = int(parts[1])
            total += val
            if total > limit and not limit_exceeded:
              print(
                  f"[SHADOW] Тіньовий ліміт перевищено ({total} > {limit})."
                  " Активую схему."
              )
              limit_exceeded = True
          except ValueError:
            pass
        print(f"-> Лог елемента: {item}")
        yield item

    return wrapper
  return decorator

def suspicious_counter(threshold=100):
  def decorator(func):
    def wrapper(*args, **kwargs):
      suspicious_total = 0
      for item in func(*args, **kwargs):
        parts = item.split()
        if len(parts) == 2:
          try:
            val = int(parts[1])
            if "refund" in parts[0] or val > threshold:
              suspicious_total += val
              print(
                  f"[COUNTER] Підозріла активність! Накопичено:"
                  f" {suspicious_total}"
              )
          except ValueError:
            pass
        yield item

    return wrapper
  return decorator


@suspicious_counter(threshold=150)
@shadow(limit=200)
def run_system():
  return transaction_stream()


if __name__ == "__main__":
  for tx in run_system():
    pass