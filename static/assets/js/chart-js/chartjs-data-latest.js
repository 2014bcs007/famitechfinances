var MONTHS={'01':"January", '02':"February", '03':"March", '04':"April", '05':"May", '06':"June", '07':"July", '08':"August", '09':"September", '10':"October", '11':"November", '12':"December"};
var loadedChart=null;

var labels = [], paye = [], employee_nssf = [],employer_nssf=[];
payrollArrayData.forEach((item) => {
    //labels.push(MONTHS[item.month]);
    labels.push(item.short_month);
    paye.push(item.paye);
    employee_nssf.push(item.employee_nssf);
    employer_nssf.push(item.employer_nssf);
});

var data = {
    labels: labels, datasets: [{
            label: "PAYE", backgroundColor: window.chartColors.red, 
            borderColor: window.chartColors.red, data: paye, fill: false,
        }
        , {
            label: "Employee NSSF", fill: false, backgroundColor: window.chartColors.blue,
            borderColor: window.chartColors.blue, data: employee_nssf,
        }
        , {
            label: "Employer NSSF", fill: false, backgroundColor: window.chartColors.orange,
            borderColor: window.chartColors.orange, data: employer_nssf,
        }
    ]
};

        renderGraph('monthly_payroll_graph_report',data, 'bar', 'Client Payroll Statistics', 'Stats', 'Month');


function renderGraph(id,data, type = 'bar', title, yAxis, xAxis, dislayTitle = false) {
    var config = {
        type: type, data: data
        , options: {
            responsive: true, title: {
                display: dislayTitle, text: title
            }
            , tooltips: {
                mode: 'index', intersect: false,
            }
            , hover: {
                mode: 'nearest', intersect: true
            }
            , scales: {
                xAxes: [{
                        display: true, scaleLabel: {
                            display: true, labelString: xAxis
                        }
                    }
                ], yAxes: [{
                        display: true, scaleLabel: {
                            display: true, labelString: yAxis
                        }
                    }
                ]
            }
        }
    };
    if(loadedChart!=null){
        loadedChart.destroy();
    }
    var ctx = document.getElementById(id).getContext("2d");
    loadedChart = new Chart(ctx, config);
}
var randomScalingFactor = function () {
    return Math.round(Math.random() * 100);
};