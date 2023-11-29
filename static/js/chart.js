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
                hoverOffset: backgroundColor?.length
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