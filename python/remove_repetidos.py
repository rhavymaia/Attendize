import mysql.connector
from mysql.connector import Error

try:
	connection = mysql.connector.connect(host='seducitec.vpn',
										 database='attendize',
										 user='ota',
										 password='0t4c1l10')
	if connection.is_connected():
		db_Info = connection.get_server_info()
		print("Connected to MySQL Server version ", db_Info)
		cursor = connection.cursor()
		cursor.execute("select database();")
		record = cursor.fetchone()
		print("Your connected to database: ", record)

		sql_select_Query = "SELECT ticket_id, curso, email, duplicados FROM (SELECT ticket.id as ticket_id, ticket.title as curso, attendee.first_name, attendee.last_name, attendee.email as email, count(attendee.email) as duplicados FROM attendize.tickets as ticket, attendize.attendees as attendee WHERE ticket.is_hidden=0 AND attendee.ticket_id=ticket.id AND attendee.is_cancelled = 0 GROUP BY ticket.id, ticket.title, attendee.email, attendee.first_name, attendee.last_name ORDER BY ticket.title, attendee.email) AS foo WHERE duplicados>1 ORDER BY duplicados DESC;"
		cursor.execute(sql_select_Query)
		records = cursor.fetchall()
		print("Número de usuários com inscrições duplicadas: ", cursor.rowcount)

		for row in records:
			print("Removendo duplicados do ticket", row[0],  "|", row[1], "|", row[2], "|", row[3])
			# Para cada registro retornado, monte uma consulta específica. Enquanto o número de registros na consulta for
			# maior que 1 roda o script de atualização
			
			sql_select_Query = "SELECT id FROM attendize.attendees WHERE ticket_id="+str(row[0])+" AND email='"+row[2]+"' AND is_cancelled=0 ORDER BY created_at ASC;"
			cursor.execute(sql_select_Query)
			records2 = cursor.fetchall()
			row2 = records2[0]
			numduplicados = cursor.rowcount
			while(numduplicados>1):
				sql_update = "UPDATE attendize.attendees set is_cancelled=1 WHERE ticket_id="+str(row[0])+" AND email='"+row[2]+"' AND id="+str(row2[0])
				cursor.execute(sql_update)
				connection.commit()
				sql_select_Query = "SELECT * FROM attendize.attendees WHERE ticket_id="+str(row[0])+" AND email='"+row[2]+"' AND is_cancelled=0 ORDER BY created_at ASC;"
				cursor.execute(sql_select_Query)
				records2 = cursor.fetchall()
				row2 = records2[0]
				numduplicados = cursor.rowcount
				print("Numero de inscrições", numduplicados)
		# Bem, agora vamos atualizar o número de tickets vendidos
		sql_select_Query = "SELECT id, title, quantity_available, quantity_sold FROM attendize.tickets;"
		cursor.execute(sql_select_Query)
		records = cursor.fetchall()
		for row in records:
			sql_select_Query="SELECT count(*) FROM attendize.attendees WHERE ticket_id="+str(row[0])+" AND is_cancelled=0"
			cursor.execute(sql_select_Query)
			records2 = cursor.fetchall()
			row2=records2[0]
			print("Atualizando a quantidade de tickets vendidos de", row[1], " de ", row[3], " para ", row2[0])
			sql_update = "UPDATE attendize.tickets set quantity_sold="+str(row2[0])+" WHERE id="+str(row[0])
			cursor.execute(sql_update)
			connection.commit()
except Error as e:
	print("Error while connecting to MySQL", e)
finally:
	if (connection.is_connected()):
		cursor.close()
		connection.close()
		print("MySQL connection is closed")
