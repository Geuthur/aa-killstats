// eslint-disable-next-line no-undef
var corporationPk = corporationsettings.corporation_pk;
// eslint-disable-next-line no-undef
var alliancePk = corporationsettings.alliance_pk;
var selectedMonth, selectedYear;
var monthText;
var halls, stats;

// Aktuelles Datumobjekt erstellen
var currentDate = new Date();
var killsTable, lossesTable;
var urlStats, urlHalls, urlKills, urlLosses;

// Aktuelles Jahr und Monat abrufen
selectedYear = currentDate.getFullYear();
selectedMonth = currentDate.getMonth() + 1; // +1, um 1-basierten Monat zu erhalten
monthText = getMonthName(selectedMonth);

if (alliancePk) {
    urlStats = '/killstats/api/stats/month/' + selectedMonth + '/year/' + selectedYear + '/alliance/' + alliancePk + '/';
    urlHalls = '/killstats/api/halls/month/' + selectedMonth + '/year/' + selectedYear + '/alliance/' + alliancePk + '/';
    urlKills = '/killstats/api/killmail/month/' + selectedMonth + '/year/' + selectedYear + '/alliance/' + alliancePk + '/kills/';
    urlLosses = '/killstats/api/killmail/month/' + selectedMonth + '/year/' + selectedYear + '/alliance/' + alliancePk + '/losses/';
} else {
    urlStats = '/killstats/api/stats/month/' + selectedMonth + '/year/' + selectedYear + '/corporation/' + corporationPk + '/';
    urlHalls = '/killstats/api/halls/month/' + selectedMonth + '/year/' + selectedYear + '/corporation/' + corporationPk + '/';
    urlKills = '/killstats/api/killmail/month/' + selectedMonth + '/year/' + selectedYear + '/corporation/' + corporationPk + '/kills/';
    urlLosses = '/killstats/api/killmail/month/' + selectedMonth + '/year/' + selectedYear + '/corporation/' + corporationPk + '/losses/';
}

function getUrl() {
    if (alliancePk) {
        urlStats = '/killstats/api/stats/month/' + selectedMonth + '/year/' + selectedYear + '/alliance/' + alliancePk + '/';
        urlHalls = '/killstats/api/halls/month/' + selectedMonth + '/year/' + selectedYear + '/alliance/' + alliancePk + '/';
        urlKills = '/killstats/api/killmail/month/' + selectedMonth + '/year/' + selectedYear + '/alliance/' + alliancePk + '/kills/';
        urlLosses = '/killstats/api/killmail/month/' + selectedMonth + '/year/' + selectedYear + '/alliance/' + alliancePk + '/losses/';
    } else {
        urlStats = '/killstats/api/stats/month/' + selectedMonth + '/year/' + selectedYear + '/corporation/' + corporationPk + '/';
        urlHalls = '/killstats/api/halls/month/' + selectedMonth + '/year/' + selectedYear + '/corporation/' + corporationPk + '/';
        urlKills = '/killstats/api/killmail/month/' + selectedMonth + '/year/' + selectedYear + '/corporation/' + corporationPk + '/kills/';
        urlLosses = '/killstats/api/killmail/month/' + selectedMonth + '/year/' + selectedYear + '/corporation/' + corporationPk + '/losses/';
    }
    return { urlKills, urlLosses, urlStats, urlHalls };
}

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
        $('#shame-nav').show(); // Container für Hall of Shame anzeigen
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
                                <a href="${kill.zkb_link}" target="_blank">
                                    <img class="card-img-zoom" src="${kill.portrait}">
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

// Funktion zum Setzen des aktiven Tabs
function setActiveTab(tab) {
    if (tab === 'shame') {
        $('#shame-nav').addClass('active');
        $('#fame-nav').removeClass('active');
        $('#tab-shame').addClass('active show');
        $('#tab-fame').removeClass('active show');
    } else if (tab === 'fame') {
        $('#fame-nav').addClass('active');
        $('#shame-nav').removeClass('active');
        $('#tab-fame').addClass('active show');
        $('#tab-shame').removeClass('active show');
    }
}

// Funktion zum Ermitteln des aktiven Tabs
function getActiveTab() {
    if ($('#shame-nav').hasClass('active')) {
        return 'shame';
    } else if ($('#fame-nav').hasClass('active')) {
        return 'fame';
    }
    return null;
}

function initializeDataTable(tableId, url, totalValueId) {
    return $(tableId).DataTable({
        'processing': true,
        'serverSide': true,
        'ajax': {
            'url': url,
            'dataSrc': function(json) {
                $(totalValueId).text(json.totalvalue.toLocaleString());
                return json.data;
            }
        },
        'columns': [
            {
                'data': 'killmail_id',
                'render': function(data, type, row) {
                    return '<a href="https://zkillboard.com/kill/' + data + '" target="_blank">' +
                        '<img class="card-img-zoom" src="https://imageserver.eveonline.com/types/' + row.victim_ship.id + '/icon/?size=64" height="64" width="64"/>' +
                        '</a>';
                }
            },
            {
                'data': 'victim_ship',
                'render': function(data, type, row) {
                    return row.victim_ship.name;
                }
            },
            {
                'data': 'victim',
                'render': function (data, type, row) {
                    var imageUrl = 'https://imageserver.eveonline.com/';
                    if (data && data.id !== row.victim_alliance_id && data.id !== row.victim_corporation_id) {
                        imageUrl += 'characters/' + data.id + '/portrait/?size=64';
                    } else if (row.victim_alliance_id && data.id === row.victim_alliance_id) {
                        imageUrl += 'alliances/' + row.victim_alliance_id + '/logo/?size=64';
                    } else if (row.victim_corporation_id && data.id === row.victim_corporation_id) {
                        imageUrl += 'corporations/' + row.victim_corporation_id + '/logo/?size=64';
                    } else {
                        // Fallback image URL if no valid ID is available
                        imageUrl += 'icons/no-image.png'; // Beispiel für ein Platzhalterbild
                    }

                    var imageHTML = '<a href="https://zkillboard.com/';
                    if (data && data.id !== row.victim_alliance_id && data.id !== row.victim_corporation_id) {
                        imageHTML += 'character/' + data.id;
                    } else if (row.victim_alliance_id && data.id === row.victim_alliance_id) {
                        imageHTML += 'alliance/' + row.victim_alliance_id;
                    } else if (row.victim_corporation_id && data.id === row.victim_corporation_id) {
                        imageHTML += 'corporation/' + row.victim_corporation_id;
                    }

                    imageHTML += '" target="_blank"> <img class="card-img-zoom" src="' + imageUrl + '" height="64" width="64"/></a>';

                    return imageHTML;
                }
            },
            { 'data': 'victim.name'},
            {
                'data': 'victim_total_value',
                'render': function (data, type, row) {
                    // Rückgabe des formatierten Strings mit Farbe und Einheit
                    if (type === 'display') {
                        return data.toLocaleString() + ' ISK';
                    }
                    return data;
                }
            },
            {
                'data': 'killmail_date',
                'render': function (data, type, row) {
                    return moment(data).format('YYYY-MM-DD HH:mm'); // eslint-disable-line no-undef
                }
            },
        ],
        'order': [[5, 'desc']],
        'pageLength': 25,
        'autoWidth': false,
        'columnDefs': [
            { 'sortable': false, 'targets': [0, 2] },
        ],
    });
}

// Funktion zum Aktualisieren der Fame-Daten
function updateFame(fameData) {
    // Fügen Sie Daten in die "Hall of Fame" Tab-Inhalte ein

    // Prüfe, ob fame Daten enthält und zeige den entsprechenden Container an oder aus
    if (fameData && fameData.length > 0) {
        $('#hall').show(); // Container für Hall of Fame anzeigen
        $('#fame-nav').show(); // Container für Hall of Fame anzeigen
    } else {
        $('#fame-nav').hide(); // Container für Hall of Fame ausblenden
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
                                <a href="${kill.zkb_link}" target="_blank">
                                    <img class="card-img-zoom" src="${kill.portrait}">
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
    // Setze den aktiven Tab
    setActiveTab();
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
            // Erstelle das HTML für jede Statistik basierend auf dem Typ
            statsHtml += `
                <div class="card mb-4 px-0">
                    <div class="row g-0">`;

            // Füge den <a>-Tag hinzu, wenn character_id vorhanden ist
            if (stat.count) {
                if (stat.character_id) {
                    statsHtml += `
                            <div class="col-md-4">
                                <a href="${stat.zkb_link}" target="_blank">
                                    <img class="card-img-zoom img-fluid rounded-start" style="width: 100%; height:100%" src="${stat.portrait}">
                                </a>
                            </div>`;
                } else {
                    statsHtml += `
                            <div class="col-md-4">
                                <img class="card-img img-fluid rounded-start" style="width: 100%; height:100%" src="${stat.portrait}">
                            </div>`;
                }
            } else {
                statsHtml += `
                            <div class="col-md-4">
                                <a href="https://zkillboard.com/kill/${stat.killmail_id}" target="_blank">
                                    <img class="card-img-zoom img-fluid rounded-start" style="width: 100%; height:100%" src="${stat.portrait}">
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
    // Setze den aktiven Tab
    setActiveTab();
}

$('#monthDropdown li').click(function() {
    selectedMonth = $(this).find('a').data('bs-month-id');
    monthText = getMonthName(selectedMonth);
    var activeTab = getActiveTab();
    const { urlStats, urlKills, urlLosses, urlHalls } = getUrl();
    $('#killboard').hide();
    $('#hall').hide();
    $('#stats').hide();
    $('#loadingIndicator').removeClass('d-none');

    // AJAX-Anfrage für Kills
    killsTable.ajax.url(urlKills).load(function() {
        $('#killboard').show();
        $('#loadingIndicator').addClass('d-none');
    });

    // AJAX-Anfrage für Losses
    lossesTable.ajax.url(urlLosses).load(function() {
        $('#loadingIndicator').addClass('d-none');
    });

    // AJAX-Anfrage für Halls
    halls = $.ajax({
        url: urlHalls,
        method: 'GET',
        dataType: 'json',
        success: function (data) {
            $('#killboard').show();
            $('#loadingIndicator').addClass('d-none');
            updateShame(data[0].shame);
            updateFame(data[0].fame);
            setActiveTab(activeTab);
        }
    });

    // AJAX-Anfrage für Stats
    stats = $.ajax({
        url: urlStats,
        method: 'GET',
        dataType: 'json',
        success: function (data) {
            $('#killboard').show();
            $('#loadingIndicator').addClass('d-none');
            updateStats(data[0].stats);
        }
    });

    $('#currentMonthLink').text('Killboard Month - ' + monthText);
});

document.addEventListener('DOMContentLoaded', function () {
    // AJAX-Anfrage für Statsq
    stats = $.ajax({
        url: urlStats,
        method: 'GET',
        dataType: 'json',
        success: function (data) {
            // Zeige den Killboard-Container an
            $('#killboard').show();
            $('#loadingIndicator').addClass('d-none');
            // Daten für Stats aktualisieren
            updateStats(data[0].stats);
        },
        error: function (xhr, status, error) {
            console.error('AJAX Error:', error);
            // Hier können Sie Fehlerbehandlung implementieren
        }
    });
    // AJAX-Anfrage für Stats
    halls = $.ajax({
        url: urlHalls,
        method: 'GET',
        dataType: 'json',
        success: function (data) {
            // Zeige den Killboard-Container an
            $('#killboard').show();
            $('#loadingIndicator').addClass('d-none');
            // Daten für Hall of Shame aktualisieren
            updateShame(data[0].shame);
            // Daten für Hall of Fame aktualisieren
            updateFame(data[0].fame);
        }
    });

    // Initialisieren Sie die DataTable für kills
    killsTable = initializeDataTable('#kills', urlKills, '#total-value-kills');

    // Initialisieren Sie die DataTable für losses
    lossesTable = initializeDataTable('#losses', urlLosses, '#total-value-losses');

});
