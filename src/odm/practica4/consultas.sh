# Cambiar el ejecutable de python por el del sistema
# Consulta 1
echo "Consulta 1"
cat ./apache.log | python3 funciones1/map.py | python3 funciones1/reduce.py

# Consulta 2
echo "Consulta 2"
cat ./apache.log | python3 funciones2/map.py | sort | python3 funciones2/reduce.py

# Consulta 3
echo "Consulta 3"
cat ./apache.log | python3 funciones3/map.py | sort | python3 funciones3/reduce.py

# Consulta 4
echo "Consulta 4"
cat ./apache.log | python3 funciones4/map.py | sort | python3 funciones4/reduce.py

# Consulta 5
echo "Consulta 5"
cat ./apache.log | python3 funciones5/map.py | sort | python3 funciones5/reduce.py

# Consulta 6
echo "Consulta 6"
cat ./apache.log | python3 funciones6/map.py | sort | python3 funciones6/reduce.py

# Consulta 7
echo "Consulta 7"
cat ./apache.log | python3 funciones7/map.py | sort | python3 funciones7/reduce.py

# Consulta 8
echo "Consulta 8"
cat ./apache.log | python3 funciones8/map.py | sort | python3 funciones8/reduce.py

# Consulta 9
echo "Consulta 9"
cat ./apache.log | python3 funciones9/map.py | sort | python3 funciones9/reduce.py