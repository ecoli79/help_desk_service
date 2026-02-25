import db_working
import bot


#tickets = db_working.get_tickets()

# for ticket in tickets:
#     print(ticket[0])

    
ticket_types = db_working.get_ticket_types()
#print(ticket_types)
for type in ticket_types:
    print(type[0])

ticket_types = ['Подписание', 'Оборудование', 'Доступ к системам', 'Другое']

tickets = ' '.join(ticket_types)

print(tickets)