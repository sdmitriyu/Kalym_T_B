def filter_orders_for_contractor(contractor, orders):
    """
    Фильтрует список заказов для подрядчика по совпадению услуг и территории.
    contractor: dict с ключами 'services' и 'territory'
    orders: список dict с ключами 'services' и 'territory'
    Возвращает список подходящих заказов.
    """
    contractor_services = set(map(str.strip, contractor.get("services", "").lower().split(",")))
    contractor_territory = set(map(str.strip, contractor.get("territory", "").lower().split(",")))
    filtered = []
    for order in orders:
        order_services = set(map(str.strip, order.get("services", "").lower().split(",")))
        order_territory = set(map(str.strip, order.get("territory", "").lower().split(",")))
        if contractor_services & order_services and contractor_territory & order_territory:
            filtered.append(order)
    return filtered

def filter_services_for_customer(order, services):
    """
    Фильтрует список услуг для заказчика по совпадению услуг и территории.
    order: dict с ключами 'services' и 'territory'
    services: список dict с ключами 'services' и 'territory'
    Возвращает список подходящих услуг.
    """
    order_services = set(map(str.strip, order.get("services", "").lower().split(",")))
    order_territory = set(map(str.strip, order.get("territory", "").lower().split(",")))
    filtered = []
    for service in services:
        contractor_services = set(map(str.strip, service.get("services", "").lower().split(",")))
        contractor_territory = set(map(str.strip, service.get("territory", "").lower().split(",")))
        if order_services & contractor_services and order_territory & contractor_territory:
            filtered.append(service)
    return filtered 