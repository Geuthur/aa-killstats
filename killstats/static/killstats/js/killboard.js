var selectedMonth, selectedYear;
var monthText;

// Aktuelles Datumobjekt erstellen
var currentDate = new Date();
var killsTable, lossesTable;

// Aktuelles Jahr und Monat abrufen
selectedYear = currentDate.getFullYear();
selectedMonth = currentDate.getMonth() + 1; // +1, um 1-basierten Monat zu erhalten
monthText = getMonthName(selectedMonth);

function getMonthName(monthNumber) {
    var months = ['January', 'February', 'March', 'April', 'May', 'June',
        'July', 'August', 'September', 'October', 'November', 'December'];
    return months[monthNumber - 1]; // Array ist 0-basiert, daher -1
};

// Funktion zum Aktualisieren der Shame-Daten
function updateShame(shameData) {
    // Fügen Sie Daten in die "Hall of Shame" Tab-Inhalte ein

    // Prüfe, ob shame Daten enthält und zeige den entsprechenden Container an oder aus
    if (shameData && shameData.length > 0) {
        $('#hall').show(); // Container für Hall of Shame anzeigen
    } else {
        $('#hall').hide(); // Container für Hall of Shame ausblenden
    }

    // Prüfe, ob shame Daten enthält und zeige den entsprechenden Container an oder aus
    if (shameData && shameData.length > 0) {
        $('#shame-nav').show(); // Container für Hall of Shame anzeigen
        if (!$('#shame-nav').hasClass('active') && !$('#fame-nav').hasClass('active')) {
            $('#shame-nav').addClass('active');
        }
    } else {
        $('#shame-nav').hide(); // Container für Hall of Shame ausblenden
        $('#shame-nav').removeClass('active');
    }

    if (shameData) {

        var shameTabContent = '';
        shameData.forEach(function (kill) {
            shameTabContent += `
                <li class="cards_item">
                    <div class="card">
                        <div class="card-header">${kill.character_name}</div>
                        <div class="card-body">
                            <span class="hall-character-image">
                                <a href="https://zkillboard.com/character/${kill.character_id}" target="_blank">
                                    <img class="card-img-zoom" src="https://images.evetech.net/characters/${kill.character_id}/portrait?size=256">
                                </a>
                                <span class="ship-logo">
                                    <a href="https://zkillboard.com/kill/${kill.killmail_id}" target="_blank">
                                        <img class="card-img-zoom shop-logo" src="https://images.evetech.net/Render/${kill.ship}_64.png">
                                    </a>
                                </span>
                            </span>
                        </div>
                        <div class="card-footer">
                            <span>${kill.totalValue.toLocaleString()}</span> ISK <br>
                            ${kill.ship_name} <br><br>
                            <a class="btn btn-primary btn-sm" href="https://zkillboard.com/kill/${kill.killmail_id}" target="_blank">Killmail</a>
                        </div>
                    </div>
                </li>
            `;
        });
        $('#tab-shame .cards_container').html(shameTabContent);
    }
}

// Funktion zum Aktualisieren der Fame-Daten
function updateFame(fameData) {
    // Fügen Sie Daten in die "Hall of Fame" Tab-Inhalte ein

    // Prüfe, ob shame Daten enthält und zeige den entsprechenden Container an oder aus
    if (fameData && fameData.length > 0) {
        $('#fame-nav').show(); // Container für Hall of Shame anzeigen
        if (!$('#fame-nav').hasClass('active') && !$('#shame-nav').hasClass('active')) {
            $('#fame-nav').addClass('active');
            $('#tab-fame').show(); // Container für Hall of Shame anzeigen
        }
    } else {
        $('#fame-nav').hide(); // Container für Hall of Shame ausblenden
        $('#fame-nav').removeClass('active');
    }

    if (fameData) {
        var fameTabContent = '';
        fameData.forEach(function (kill) {
            fameTabContent += `
                <li class="cards_item">
                    <div class="card">
                        <div class="card-header">${kill.character_name}</div>
                        <div class="card-body">
                            <span class="hall-character-image">
                                <a href="https://zkillboard.com/character/${kill.character_id}" target="_blank">
                                    <img class="card-img-zoom" src="https://images.evetech.net/characters/${kill.character_id}/portrait?size=256">
                                </a>
                                <span class="ship-logo">
                                    <a href="https://zkillboard.com/kill/${kill.killmail_id}" target="_blank">
                                        <img class="card-img-zoom shop-logo" src="https://images.evetech.net/Render/${kill.ship}_64.png">
                                    </a>
                                </span>
                            </span>
                        </div>
                        <div class="card-footer">
                            <span>${kill.totalValue.toLocaleString()}</span> ISK <br>
                            ${kill.ship_name} <br><br>
                            <a class="btn btn-primary btn-sm" href="https://zkillboard.com/kill/${kill.killmail_id}" target="_blank">Killmail</a>
                        </div>
                    </div>
                </li>
            `;
        });
        $('#tab-fame .cards_container').html(fameTabContent);
    }
}

// Funktion zum Aktualisieren der Stats-Daten
function updateStats(statsData) {
    // Überprüfen, ob Statistikdaten vorhanden sind

    // Prüfe, ob stats Daten enthält und zeige den entsprechenden Container an oder aus
    if (statsData && statsData.length > 0) {
        $('#stats').show(); // Container für Statistiken anzeigen
    } else {
        $('#stats').hide(); // Container für Statistiken ausblenden
    }

    if (statsData) {
        var statsContainer = $('.stats .row');
        var statsHtml = '';

        // Iterieren Sie über die Statistikdaten und erstellen Sie das HTML
        statsData.forEach(function (stat) {
            var imageUrl = '';
            if (stat.type === 'count') {
                if (stat.character_id) {
                    imageUrl = `https://images.evetech.net/characters/${stat.character_id}/portrait?size=256`;
                } else {
                    imageUrl = `https://imageserver.eveonline.com/Render/${stat.ship}_256.png`;
                }
            } else {
                if (stat.type === 'ship') {
                    imageUrl = `https://imageserver.eveonline.com/Render/${stat.ship}_256.png`;
                } else {
                    if (stat.character_id != stat.corporation_id) {
                        imageUrl = `https://images.evetech.net/characters/${stat.character_id}/portrait?size=256`;
                    } else {
                        imageUrl = `https://imageserver.eveonline.com/Render/${stat.ship}_256.png`;
                    }
                }
            }

            // Erstelle das HTML für jede Statistik basierend auf dem Typ
            statsHtml += `
                <div class="card mb-4 px-0">
                    <div class="row g-0">`;

            // Füge den <a>-Tag hinzu, wenn character_id vorhanden ist
            if (stat.count) {
                if (stat.character_id) {
                    statsHtml += `
                            <div class="col-md-4">
                                <a href="https://zkillboard.com/character/${stat.character_id}" target="_blank">
                                    <img class="card-img-zoom img-fluid rounded-start" style="width: 100%; height:100%" src="${imageUrl}">
                                </a>
                            </div>`;
                } else {
                    statsHtml += `
                            <div class="col-md-4">
                                <img class="card-img img-fluid rounded-start" style="width: 100%; height:100%" src="${imageUrl}">
                            </div>`;
                }
            } else {
                statsHtml += `
                            <div class="col-md-4">
                                <a href="https://zkillboard.com/kill/${stat.killmail_id}" target="_blank">
                                    <img class="card-img-zoom img-fluid rounded-start" style="width: 100%; height:100%" src="${imageUrl}">
                                </a>
                            </div>`;
            }

            statsHtml += `
                    <div class="col-md-8">
                        <div class="card-body">
                            <h5 class="card-title">${stat.title} ${stat.ship_name ? stat.ship_name : ''}</h5>`;

            if (stat.type === 'count') {
                statsHtml += `<p>${stat.loss ? 'Deaths' : 'Kills'}: ${stat.count}</p>`;
            } else {
                statsHtml += `<span class="dashboard-item-value">${stat.totalValue.toLocaleString()} ISK</span>`;
            }

            statsHtml += `
                            </div>
                        </div>
                    </div>
                </div>`;
        });

        // Fügen Sie das erstellte HTML in das Container-Element ein
        statsContainer.html(statsHtml);
    }
}

$('#monthDropdown li').click(function() {
    selectedMonth = $(this).find('a').data('bs-month-id');
    monthText = getMonthName(selectedMonth);

    $('#killboard').hide();
    $('#hall').hide();
    $('#stats').hide();
    $('#loadingIndicator').removeClass('d-none');

    // URL für die Daten der ausgewählten Kombination von Jahr und Monat erstellen
    var url = '/killstats/api/killboard/month/' + selectedMonth + '/year/' + selectedYear + '/';

    // DataTable neu laden mit den Daten des ausgewählten Monats
    var currentMonthTable = $.ajax({
        url: url,
        method: 'GET',
        dataType: 'json',
        success: function (data) {
            $('#killboard').show();
            $('#loadingIndicator').addClass('d-none');
            // Zusätzliche Daten im DataTable-Objekt speichern
            $('#total-value-kills').text(data[0].totalKills.toLocaleString());
            $('#total-value-losses').text(data[0].totalLoss.toLocaleString());

            killsTable.clear().rows.add(data[0].kills).draw();
            // Daten für die Kills-Tabelle aktualisieren
            lossesTable.clear().rows.add(data[0].losses).draw();

            // Daten für Shame aktualisieren
            updateShame(data[0].shame);

            // Daten für Fame aktualisieren
            updateFame(data[0].fame);

            // Daten für Stats aktualisieren
            updateStats(data[0].stats);

        },
        error: function (xhr, status, error) {
            console.error('AJAX Error:', error);
            $('#loadingIndicator').addClass('d-none');
            // Hier können Sie Fehlerbehandlung implementieren
        }
    });
    $('#currentMonthLink').text('Killboard Month - ' + monthText);
});

document.addEventListener('DOMContentLoaded', function () {
    var url = '/killstats/api/killboard/month/' + selectedMonth + '/year/' + selectedYear + '/';

    // AJAX-Anfrage, um Daten für kills und losses abzurufen
    var currentMonthTable = $.ajax({
        url: url,
        method: 'GET',
        dataType: 'json',
        success: function (data) {
            // Zeige den Killboard-Container an
            $('#killboard').show();
            $('#loadingIndicator').addClass('d-none');
            // Zusätzliche Daten im DataTable-Objekt speichern
            $('#total-value-kills').text(data[0].totalKills.toLocaleString());
            $('#total-value-losses').text(data[0].totalLoss.toLocaleString());

            // Initialisieren Sie die DataTable für kills
            killsTable = $('#kills').DataTable({
                data: data[0].kills,
                columns: [
                    {
                        data: 'col-killmail',
                        render: function (data, type, row) {
                            var imageHTML = '<a href="https://zkillboard.com/kill/' + row.killmail_id + '" target="_blank"> <img class="card-img-zoom" src="https://imageserver.eveonline.com/types/' + row.ship + '/icon/?size=64" height="64" width="64"/></a>';
                            return imageHTML;
                        }
                    },
                    // Add more columns as needed
                    {
                        data: 'col-type',
                        render: function (data, type, row) {
                            var imageHTML = row.ship_name;
                            return imageHTML;
                        }
                    },
                    {
                        data: 'col-portrait',
                        render: function (data, type, row) {
                            var idToUse = row.character_id || row.corporation_id || row.alliance_id;
                            var imageUrl = 'https://imageserver.eveonline.com/';

                            if (row.character_id) {
                                imageUrl += 'characters/' + row.character_id + '/portrait/?size=64';
                            } else if (row.alliance_id) {
                                imageUrl += 'alliances/' + row.alliance_id + '/logo/?size=64';
                            } else if (row.corporation_id) {
                                imageUrl += 'corporations/' + row.corporation_id + '/logo/?size=64';
                            } else {
                                // Fallback image URL if no valid ID is available
                                imageUrl += 'icons/no-image.png'; // Beispiel für ein Platzhalterbild
                            }

                            var imageHTML = '<a href="https://zkillboard.com/';
                            if (row.character_id) {
                                imageHTML += 'character/' + row.character_id;
                            } else if (row.alliance_id) {
                                imageHTML += 'alliance/' + row.alliance_id;
                            } else if (row.corporation_id) {
                                imageHTML += 'corporation/' + row.corporation_id;
                            }
                            imageHTML += '" target="_blank"> <img class="card-img-zoom" src="' + imageUrl + '" height="64" width="64"/></a>';

                            return imageHTML;
                        }
                    },
                    {
                        data: 'col-character',
                        render: function (data, type, row) {
                            var imageHTML = row.name;
                            return imageHTML;
                        }
                    },
                    {
                        data: 'col-totalvalue',
                        render: function (data, type, row) {
                            // Rückgabe des formatierten Strings mit Farbe und Einheit
                            if (type === 'display') {
                                return row.totalValue.toLocaleString() + ' ISK';
                            }
                            return row.totalValue;
                        }
                    },
                    {
                        data: 'col-date',
                        render: function (data, type, row) {
                            var imageHTML = moment(row.date).format('YYYY-MM-DD HH:mm'); // eslint-disable-line no-undef
                            return imageHTML;
                        }
                    },
                ],
                order: [[5, 'desc']],
                pageLength: 10,
                autoWidth: false,
                columnDefs: [
                    { sortable: false, targets: [0, 2] },
                ],
            });

            // Initialisieren Sie die DataTable für losses
            lossesTable = $('#losses').DataTable({
                data: data[0].losses,
                columns: [
                    {
                        data: 'col-killmail',
                        render: function (data, type, row) {
                            var imageHTML = '<a href="https://zkillboard.com/kill/' + row.killmail_id + '"  target="_blank"> <img class="card-img-zoom" src="https://imageserver.eveonline.com/types/' + row.ship + '/icon/?size=64" height="64" width="64"/></a>';
                            return imageHTML;
                        }
                    },
                    // Add more columns as needed
                    {
                        data: 'col-type',
                        render: function (data, type, row) {
                            var imageHTML = row.ship_name;
                            return imageHTML;
                        }
                    },
                    {
                        data: 'col-portrait',
                        render: function (data, type, row) {
                            var imageHTML = '<a href="https://zkillboard.com/character/' + row.character_id + '"  target="_blank"> <img class="card-img-zoom" src="https://imageserver.eveonline.com/characters/' + row.character_id + '/portrait/?size=64" height="64" width="64"/></a>';
                            return imageHTML;
                        }
                    },
                    {
                        data: 'col-character',
                        render: function (data, type, row) {
                            var imageHTML = row.name;
                            return imageHTML;
                        }
                    },
                    {   data: 'col-totalvalue',
                        render: function (data, type, row) {
                            // Rückgabe des formatierten Strings mit Farbe und Einheit
                            if (type === 'display') {
                                return row.totalValue.toLocaleString() + ' ISK';
                            }
                            return row.totalValue;
                        }
                    },
                    {
                        data: 'col-date',
                        render: function (data, type, row) {
                            var imageHTML = moment(row.date).format('YYYY-MM-DD HH:mm'); // eslint-disable-line no-undef
                            return imageHTML;
                        }
                    },
                ],
                order: [[5, 'desc']],
                pageLength: 10,
                autoWidth: false,
                columnDefs: [
                    { sortable: false, targets: [0, 2] },
                ],
            });

            // Daten für Shame aktualisieren
            updateShame(data[0].shame);

            // Daten für Fame aktualisieren
            updateFame(data[0].fame);

            // Daten für Stats aktualisieren
            updateStats(data[0].stats);

        },
        error: function (xhr, status, error) {
            console.error('AJAX Error:', error);
            // Hier können Sie Fehlerbehandlung implementieren
        }
    });
});
