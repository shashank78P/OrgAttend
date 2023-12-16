let DayInNumber = {
    Sun: 0, Mon: 1, Tue: 2, Wed: 3, Thu: 4, Fri: 5, Sat: 6,
}

let attendance_calendar_form = document.getElementById("attendance_calendar_form");
let calender_year_filter = document.getElementById("calender_year_filter");
let calender_year_filter_inpt = document.getElementById("calender_year_filter_inpt");
let month_title = document.getElementsByClassName("month_title");

let currentYear = calender_year_filter_inpt.value
console.log(calender_year_filter_inpt)
console.log(calender_year_filter_inpt.value)
calender_year_filter && (calender_year_filter.innerText = currentYear)

const currentYearDecrement = () => {
    currentYear -= 1;
    // getData(currentYear)
    calender_year_filter && (calender_year_filter.innerText = currentYear)
    calender_year_filter_inpt && (calender_year_filter_inpt.value = currentYear)
    attendance_calendar_form &&  attendance_calendar_form.submit()
}

const currentYearIncrement = () => {
    currentYear = parseInt(currentYear) + 1;
    // getData(currentYear)
    calender_year_filter && (calender_year_filter.innerText = currentYear)
    calender_year_filter_inpt && (calender_year_filter_inpt.value = currentYear)
    attendance_calendar_form && attendance_calendar_form.submit()
}


// function getData(year) {
//     let days_container = document.getElementsByClassName("days_container")
//     for (let i = 0; i < 12; i++) {
//         let startDate = new Date(year, i, 1)
//         let lastDate = new Date(year, i + 1, 0)
//         let startDay = startDate.toLocaleDateString('en-US', { weekday: 'short' });
//         let lastDay = lastDate.toLocaleDateString('en-US', { weekday: 'short' });
//         let numberOfDaysInMonth = lastDate.getDate()
//         let totalNumberOfDiv = DayInNumber[startDay] + numberOfDaysInMonth + Math.abs(DayInNumber[lastDay] - 6)

//         days_container[i].innerHTML = ""
//         for (let j = 0; j < totalNumberOfDiv; j++) {
//             let node = document.createElement("li")
//             node.classList.add("day_box")
//             if (j >= DayInNumber[startDay] && j < (numberOfDaysInMonth + DayInNumber[startDay])) {
//                 node.classList.add("present")
//             }
//             days_container[i]?.appendChild(node)
//         }
//     }
// }

// getData(currentYear)