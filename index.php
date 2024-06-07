<!DOCTYPE html>
<html lang="fr">
<head>
    <meta charset="UTF-8">
    <title>Tableau Dynamique</title>
    <script src="https://unpkg.com/vue@3/dist/vue.global.prod.js"></script>
    <link href="https://unpkg.com/tailwindcss@^2.0/dist/tailwind.min.css" rel="stylesheet">
    <link href="https://cdn.jsdelivr.net/npm/flatpickr/dist/flatpickr.min.css" rel="stylesheet">
    <style>
        th {
            position: sticky;
            top: 0;
            background: white;
            z-index: 10;
        }
        .sticky-top {
            position: sticky;
            top: 0;
            background: white;
            z-index: 20;
            padding-top: 1rem;
            padding-bottom: 1rem;
        }
    </style>
</head>
<body class="bg-gray-100 text-gray-900">
    <div id="app" class="container mx-auto p-4">
        <div class="sticky-top mb-4 flex justify-between items-center bg-white shadow-md p-4 rounded-md">
            <div class="flex flex-wrap items-center">
                <!-- Bouton pour afficher toutes les données combinées -->
                <button @click="combineAllData" class="bg-blue-500 text-white px-4 py-2 rounded-md mr-2 mb-2 shadow hover:bg-blue-600 transition duration-300">
                    All
                </button>

                <!-- Input pour la sélection de date -->
                <input id="date-picker" type="text" class="bg-gray-200 text-gray-800 px-4 py-2 rounded-md mr-2 mb-2 shadow border border-gray-300" placeholder="Select Date">

                <!-- Bouton pour isoler les imprimantes -->
                <button @click="togglePrinterFilter" 
                        :class="[printerFilterActive ? 'bg-red-500' : 'bg-green-500', 'text-white', 'px-4', 'py-2', 'rounded-md', 'mr-2', 'mb-2', 'shadow', 'transition', 'duration-300']">
                    {{ printerFilterActive ? 'Show All' : 'Isolate Printers' }}
                </button>
            </div>
            <div class="flex flex-wrap items-center text-right">
                <!-- Afficher les montants pour chaque catégorie d'IPs -->
                <div class="px-4 py-2 rounded-md bg-blue-400 text-white mr-2 mb-2 shadow">
                    Printers: {{ totalPrinters }}
                </div>
                <div class="px-4 py-2 rounded-md bg-red-400 text-white mr-2 mb-2 shadow">
                    Occupied IPs: {{ totalOccupiedIPs }}
                </div>
                <div class="px-4 py-2 rounded-md bg-green-400 text-white mr-2 mb-2 shadow">
                    Available IPs: {{ totalAvailableIPs }}
                </div>
            </div>
        </div>

        <div class="overflow-x-auto">
            <table class="min-w-full bg-white shadow-md rounded-lg overflow-hidden">
                <thead class="bg-gray-50">
                    <tr>
                        <th class="py-2 px-4">IP Address</th>
                        <th class="py-2 px-4">Hostname</th>
                        <th class="py-2 px-4">MAC Address</th>
                        <th class="py-2 px-4">Manufacturer</th>
                        <th class="py-2 px-4">Is Printer</th>
                        <th class="py-2 px-4">OS Info</th>
                    </tr>
                </thead>
                <tbody>
                    <tr v-for="item in currentData" :key="item.ip_address" 
                        :class="{
                            'bg-blue-400': item.is_printer === 'Yes', 
                            'bg-red-400': item.fromJson && item.is_printer !== 'Yes', 
                            'bg-green-400': !item.fromJson && item.is_printer !== 'Yes'
                        }">
                        <td class="border-t py-2 px-4">{{ item.ip_address }}</td>
                        <td class="border-t py-2 px-4">{{ item.hostname }}</td>
                        <td class="border-t py-2 px-4">{{ item.mac_address }}</td>
                        <td class="border-t py-2 px-4">{{ item.manufacturer }}</td>
                        <td class="border-t py-2 px-4">{{ item.is_printer }}</td>
                        <td class="border-t py-2 px-4">{{ item.os_info }}</td>
                    </tr>
                </tbody>
            </table>
        </div>
    </div>
    <script src="https://cdn.jsdelivr.net/npm/flatpickr"></script>
    <script src="app.js"></script>
</body>
</html>
