// eslint-disable-next-line no-undef
var corporationPk = corporationsettings.corporation_pk;
// eslint-disable-next-line no-undef
var alliancePk = corporationsettings.alliance_pk;
var selectedMonth, selectedYear;
var monthText;
var halls, stats;
var urls, urlVictim, urlAllVictim, urlKiller, urlAllKiller, urlWorstShip, urlTopShip, urlHalls, urlKills, urlLosses;

// Aktuelles Datumobjekt erstellen
var currentDate = new Date();
var killsTable, lossesTable;

// Aktuelles Jahr und Monat abrufen
selectedYear = currentDate.getFullYear();
selectedMonth = currentDate.getMonth() + 1; // +1, um 1-basierten Monat zu erhalten
monthText = getMonthName(selectedMonth);

function generateUrl(type, entity, entityPk, selectedMonth, selectedYear) {
    return `/killstats/api/${type}/month/${selectedMonth}/year/${selectedYear}/${entity}/${entityPk}/`;
}

function getUrls(entity, entityPk, selectedMonth, selectedYear) {
    return {
        urlHalls: generateUrl('halls', entity, entityPk, selectedMonth, selectedYear),

        urlKills: generateUrl('killmail', entity, entityPk, selectedMonth, selectedYear) + 'kills/',
        urlLosses: generateUrl('killmail', entity, entityPk, selectedMonth, selectedYear) + 'losses/',

        urlVictim: generateUrl('stats/top/victim', entity, entityPk, selectedMonth, selectedYear),
        urlAllVictim: generateUrl('stats/top/alltime_victim', entity, entityPk, selectedMonth, selectedYear),

        urlKiller: generateUrl('stats/top/killer', entity, entityPk, selectedMonth, selectedYear),
        urlAllKiller: generateUrl('stats/top/alltime_killer', entity, entityPk, selectedMonth, selectedYear),

        urlWorstShip: generateUrl('stats/ship/worst', entity, entityPk, selectedMonth, selectedYear),
        urlTopShip: generateUrl('stats/ship/top', entity, entityPk, selectedMonth, selectedYear),

        urlHighestKill: generateUrl('stats/top/kill', entity, entityPk, selectedMonth, selectedYear),
        urlHighestLoss: generateUrl('stats/top/loss', entity, entityPk, selectedMonth, selectedYear),

        urlTop10: generateUrl('stats/top/10', entity, entityPk, selectedMonth, selectedYear)
    };
}

function getUrl() {
    if (alliancePk) {
        return getUrls('alliance', alliancePk, selectedMonth, selectedYear);
    } else {
        return getUrls('corporation', corporationPk, selectedMonth, selectedYear);
    }
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
function updateStats(stat, container) {
    // Überprüfen, ob Statistikdaten vorhanden sind

    // Prüfe, ob stats Daten enthält und zeige den entsprechenden Container an oder aus
    if (stat) {
        $('#stats').show(); // Container für Statistiken anzeigen
    } else {
        $('#stats').hide(); // Container für Statistiken ausblenden
        return;
    }

    var template = $('#stat-template').clone().removeAttr('id').show();

    // Füge den <a>-Tag hinzu, wenn character_id vorhanden ist
    if (stat.character_id) {
        template.find('.stat-link').attr('href', stat.zkb_link);
        template.find('.stat-portrait').attr('src', stat.portrait);
    } else {
        template.find('.stat-link').removeAttr('href');
        template.find('.stat-portrait').attr('src', stat.portrait);
    }

    template.find('.stat-title').text(`${stat.title} ${stat.ship_name ? stat.ship_name : ''}`);

    if (stat.type === 'count') {
        template.find('.stat-info').text(`${stat.loss ? 'Deaths' : 'Kills'}: ${stat.count}`);
    } else {
        template.find('.stat-info').text(`${stat.totalValue.toLocaleString()} ISK`);
    }

    // Fügen Sie das erstellte HTML in das Container-Element ein
    container.append(template);

    // Setze den aktiven Tab
    setActiveTab();
}

function loadStats(url, container) {
    stats = $.ajax({
        url: url,
        method: 'GET',
        dataType: 'json',
        success: function (data) {
            $('#killboard').show();
            $('#loadingIndicator').addClass('d-none');
            updateStats(data[0].stats, container);
        }
    });
}

function updateData(selectedMonth, selectedYear) {
    var urls;
    var activeTab = getActiveTab();

    if (alliancePk) {
        urls = getUrls('alliance', alliancePk, selectedMonth, selectedYear);
    } else {
        urls = getUrls('corporation', corporationPk, selectedMonth, selectedYear);
    }

    const { urlHalls, urlKills, urlLosses, urlVictim, urlAllVictim, urlKiller, urlAllKiller, urlWorstShip, urlTopShip, urlHighestKill, urlHighestLoss, urlTop10 } = urls;

    $('#killboard').hide();
    $('#hall').hide();
    $('#stats').hide();
    $('#loadingIndicator').removeClass('d-none');

    // Entferne alle Statistiken im #stats-Container
    $('#stats').empty();

    // Initialisiere die DataTables nur, wenn sie noch nicht initialisiert sind
    if (!$.fn.DataTable.isDataTable('#kills')) {
        killsTable = initializeDataTable('#kills', urlKills, '#total-value-kills');
    } else {
        killsTable.ajax.url(urlKills).load();
    }

    if (!$.fn.DataTable.isDataTable('#losses')) {
        lossesTable = initializeDataTable('#losses', urlLosses, '#total-value-losses');
    } else {
        lossesTable.ajax.url(urlLosses).load();
    }

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

    // Predefined order for the stats
    var statsOrder = [
        { url: urlWorstShip, container: $('#stats'), id: 'worst-ship' },
        { url: urlTopShip, container: $('#stats'), id: 'top-ship' },
        { url: urlVictim, container: $('#stats'), id: 'victim' },
        { url: urlKiller, container: $('#stats'), id: 'killer' },
        { url: urlAllVictim, container: $('#stats'), id: 'all-victim' },
        { url: urlAllKiller, container: $('#stats'), id: 'all-killer' },
        { url: urlHighestKill, container: $('#stats'), id: 'highest-kill' },
        { url: urlHighestLoss, container: $('#stats'), id: 'highest-loss' }
    ];

    // Load stats in the predefined order
    statsOrder.forEach(function (stat) {
        // Create a container for each stat if it doesn't exist
        if ($('#' + stat.id).length === 0) {
            stat.container.append('<div id="' + stat.id + '" class="col"></div>');
        }
        loadStats(stat.url, $('#' + stat.id));
    });
    $('#top10').html('<button type="button" class="btn btn-secondary" data-bs-toggle="modal" data-bs-target="#modalViewTop10KillerContainer" data-ajax_url="' + urlTop10 + '">Top 10</button>');
}

$('#monthDropdown li').click(function() {
    selectedMonth = $(this).find('a').data('bs-month-id');
    monthText = getMonthName(selectedMonth);
    updateData(selectedMonth, selectedYear);

    $('#currentMonthLink').text('Killboard Month - ' + monthText);
});

document.addEventListener('DOMContentLoaded', function () {
    var activeTab = getActiveTab();
    updateData(selectedMonth, selectedYear);
});
