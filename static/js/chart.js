function createChart(type , id , data , label , backgroundColor){
    console.log({type , id , data , label , backgroundColor})
    console.log(document.getElementById(id))
    new Chart(document.getElementById(id), {
        type: type,
        data: data = {
            // labels: [
            //     'Red',
            //     'Blue',
            //     'Yellow'
            // ],
            datasets: [{
                label: label,
                data: data,
                backgroundColor: backgroundColor,
                hoverOffset: backgroundColor?.length,
                borderColor: [
                    'rgb(255, 99, 132)',
                    'rgb(255, 159, 64)',
                    'rgb(255, 205, 86)',
                    'rgb(75, 192, 192)',
                    'rgb(54, 162, 235)',
                    'rgb(153, 102, 255)',
                    'rgb(201, 203, 207)'
                ],
                borderWidth: 1
            }]
        },
        // options: {
        //     scales: {
        //         y: {
        //             beginAtZero: true
        //         }
        //     }
        // }
    });
}