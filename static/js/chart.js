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
                borderColor: backgroundColor,
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