document.addEventListener('DOMContentLoaded', function() {
    // Gráfico 1: Quantidade de alunos por turma versus a quantidade de respondentes por turma
    var options1 = {
        chart: {
            type: 'bar',
            height: 350
        },
        plotOptions: {
            bar: {
                borderRadius: 4, // Adiciona bordas arredondadas
                columnWidth: '40%', // Ajusta a largura da coluna para adicionar espaçamento
                barGroupPadding: 10, // Espaçamento entre os grupos de barras
                dataLabels: {
                    position: 'top' // Coloca as labels no topo
                }
            }
        },
        dataLabels: {
            enabled: true,
            formatter: function(val) {
                return val;
            },
            offsetY: -20,
            style: {
                fontSize: '12px',
                colors: ["#304758"]
            }
        },
        series: [
            {
                name: 'Quantidade de Alunos',
                data: [30, 40, 35, 50, 49, 60, 70, 91]
            },
            {
                name: 'Quantidade de Respondentes',
                data: [25, 30, 27, 45, 40, 55, 65, 85]
            }
        ],
        xaxis: {
            categories: ['Turma 1', 'Turma 2', 'Turma 3', 'Turma 4', 'Turma 5', 'Turma 6', 'Turma 7', 'Turma 8']
        },
    };

    var chart1 = new ApexCharts(document.querySelector("#chart1"), options1);
    chart1.render();

    // Gráfico 2: Desempenho do usuário
var options2 = {
    chart: {
        type: 'radialBar',
        height: 350
    },
    series: [85], // Valor de desempenho para a única tarefa
    plotOptions: {
        radialBar: {
            dataLabels: {
                name: {
                    fontSize: '22px',
                },
                value: {
                    fontSize: '16px',
                },
                total: {
                    show: true,
                    label: 'Desempenho',
                    formatter: function (w) {
                        return '85%';
                    }
                }
            }
        }
    },
    labels: ['Total'], 
    
    fill: {
        type: 'gradient',
        gradient: {
          shade: 'dark',
          type: 'horizontal',
          shadeIntensity: 0.5,
          gradientToColors: ['#ABE5A1'],
          inverseColors: true,
          opacityFrom: 1,
          opacityTo: 1,
          stops: [0, 100]
        }
      },
      stroke: {
        lineCap: 'round'
      },
      labels: ['Percent'],

};

var chart2 = new ApexCharts(document.querySelector("#chart2"), options2);
chart2.render();


    // Gráfico 3: Progresso de horas de cursos feitos pelo usuário
var options3 = {
    chart: {
        type: 'bar',
        height: 300,
    },
    plotOptions: {
        bar: {
            horizontal: true,
            dataLabels: {
                position: 'top'
            }
        }
    },
    series: [
        {
            name: 'Horas Feitas',
            data: [15] // Horas completas na única semana
        }
    ],
    xaxis: {
        categories: ['Horas'], // Nome da única semana
        max: 25 // Limite máximo de 20 horas
    },
    annotations: {
        xaxis: [
            {
                x: 20,
                borderColor: '#FF4560',
                label: {
                    borderColor: '#FF4560',
                    style: {
                        color: '#fff',
                        background: '#FF4560'
                    },
                    text: '20 Horas'
                }
            }
        ]
    }
};

var chart3 = new ApexCharts(document.querySelector("#chart3"), options3);
chart3.render();

});
