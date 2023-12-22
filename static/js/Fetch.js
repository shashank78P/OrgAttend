async function fetchData( method , url , body ){
    console.log(url)
    const response =await fetch(url, {
        method: method, 
        credentials: "same-origin", 
        headers: {
            "Content-Type": "application/json",
            "X-CSRFToken" : document.cookie.split('; ').find(row => row.startsWith('csrftoken=')).split('=')[1]
        },
    });

    if (!response.ok) {
        throw new Error(`HTTP error! Status: ${response.status}`);
    }

    const data = await response.json();
    return data;
}