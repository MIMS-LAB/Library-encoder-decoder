import decoder_rrc_v2_2 as d


port = "COM2"

while True:
	try:
		d.setPort(port, "57600")
		break
	except Exception as e:
		print(e)
		port = str(input("Enter a new port number: "))
		port = "COM" + port.strip()

print("Connected")

while True:
	packet = d.getPackets()
	if packet == None:
		continue

	print('[{}]'.format(', '.join(hex(x) for x in packet)))

	result = d.decodePackets(packet)

	print("The decoded data is: " + str(result[2]))
	print("The checksums is: " + hex(result[1]))
	print("The header is: " + hex(result[0]))
	print("The time stamp is: " + str(result[3]))
	print("Data corruption: " + str(result[4]))