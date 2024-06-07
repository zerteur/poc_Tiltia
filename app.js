const { createApp } = Vue;

createApp({
    data() {
        return {
            groupedData: {},
            currentData: [],
            defaultIPs: [],
            originalData: [],
            printerFilterActive: false
        };
    },
    computed: {
        totalPrinters() {
            return this.currentData.filter(ip => ip.is_printer === 'Yes').length;
        },
        totalOccupiedIPs() {
            return this.currentData.filter(ip => ip.hostname !== 'N/A').length;
        },
        totalAvailableIPs() {
            return this.currentData.filter(ip => ip.hostname === 'N/A').length;
        }
    },
    mounted() {
        fetch('ip.php')
            .then(response => response.text())
            .then(data => {
                this.defaultIPs = data.split(',');
                this.resetToDefaultIPs();
            });

        fetch('loader_json.php')
            .then(response => response.json())
            .then(data => {
                this.groupedData = data;
                this.combineAllData();  // Appel pour combiner les données dès le chargement
                this.initializeDatePicker();  // Initialiser le date picker après le chargement des données
            });
    },
    methods: {
        initializeDatePicker() {
            flatpickr("#date-picker", {
                enable: Object.keys(this.groupedData),  // Activer seulement les dates avec des données
                dateFormat: "Y-m-d",
                onChange: this.handleDateChange
            });
        },
        handleDateChange(selectedDates, dateStr) {
            this.selectDate(dateStr);
        },
        selectDate(date) {
            this.applyDataUpdates(this.groupedData[date] || []);
        },
        resetToDefaultIPs() {
            this.currentData = this.defaultIPs.map(ip => ({
                ip_address: ip,
                hostname: 'N/A',
                mac_address: 'N/A',
                manufacturer: 'N/A',
                is_printer: 'No',  // Par défaut à 'No'
                os_info: 'N/A',
                fromJson: false  // Par défaut à false
            }));
        },
        combineAllData() {
            let combinedUpdates = {};

            // Initialisez combinedUpdates avec les IPs par défaut
            this.defaultIPs.forEach(ip => {
                combinedUpdates[ip] = {
                    ip_address: ip,
                    hostname: new Set(),
                    mac_address: new Set(),
                    manufacturer: new Set(),
                    is_printer: new Set(),
                    os_info: new Set(),
                    fromJson: false  // Par défaut à false
                };
            });

            // Combine toutes les données en un seul objet et met à jour si des données non par défaut sont trouvées
            Object.values(this.groupedData).forEach(dateData => {
                dateData.forEach(item => {
                    const ip = item.ip_address;
                    if (!combinedUpdates[ip]) {
                        combinedUpdates[ip] = {
                            ip_address: ip,
                            hostname: new Set(),
                            mac_address: new Set(),
                            manufacturer: new Set(),
                            is_printer: new Set(),
                            os_info: new Set(),
                            fromJson: true  // Marquer comme provenant du JSON
                        };
                    } else {
                        combinedUpdates[ip].fromJson = true;  // Marquer comme provenant du JSON
                    }

                    // Ajouter les valeurs aux sets pour éviter les doublons
                    if (item.hostname && item.hostname !== 'N/A') combinedUpdates[ip].hostname.add(item.hostname);
                    if (item.mac_address && item.mac_address !== 'N/A') combinedUpdates[ip].mac_address.add(item.mac_address);
                    if (item.manufacturer && item.manufacturer !== 'N/A') combinedUpdates[ip].manufacturer.add(item.manufacturer);
                    if (item.is_printer && item.is_printer !== 'N/A') combinedUpdates[ip].is_printer.add(item.is_printer === true || item.is_printer === 'Yes' ? 'Yes' : 'No');
                    if (item.os_info && item.os_info !== 'N/A') combinedUpdates[ip].os_info.add(item.os_info);
                });
            });

            // Convertit les données combinées en un tableau pour l'affichage, en joignant les sets par un point-virgule
            this.currentData = Object.values(combinedUpdates).map(ip => ({
                ip_address: ip.ip_address,
                hostname: Array.from(ip.hostname).join(' ; ') || 'N/A',
                mac_address: Array.from(ip.mac_address).join(' ; ') || 'N/A',
                manufacturer: Array.from(ip.manufacturer).join(' ; ') || 'N/A',
                is_printer: Array.from(ip.is_printer).join(' ; ') || 'No',
                os_info: Array.from(ip.os_info).join(' ; ') || 'N/A',
                fromJson: ip.fromJson
            })).sort((a, b) => a.ip_address.localeCompare(b.ip_address, undefined, { numeric: true }));

            this.originalData = [...this.currentData]; // Stockez une copie des données originales
            console.log("Current Data:", this.currentData);  // Vérifiez les données finales
        },
        togglePrinterFilter() {
            if (this.printerFilterActive) {
                this.currentData = [...this.originalData]; // Réinitialisez les données à l'original
            } else {
                this.currentData = this.originalData.filter(item => item.is_printer === 'Yes');
            }
            this.printerFilterActive = !this.printerFilterActive; // Changez l'état du filtre
        },
        applyDataUpdates(data) {
            const updates = new Map(data.map(item => [item.ip_address, item]));

            // Met à jour currentData avec des mises à jour uniques
            this.currentData = this.currentData.map(ip => {
                const update = updates.get(ip.ip_address);
                return update ? {
                    ...ip,
                    ...update,
                    is_printer: update.is_printer === true ? 'Yes' : 'No',
                    fromJson: true  // Marquer comme provenant du JSON
                } : ip;
            });
            console.log("Updated Current Data:", this.currentData);  // Vérifiez les mises à jour appliquées
        }
    }
}).mount('#app');
