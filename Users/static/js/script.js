function togglePopOver(listContainerId , buttonClass) {
    var listContainer = document.getElementById(listContainerId);
    var isOpen = listContainer.style.display === 'block';
    listContainer.style.display = isOpen ? 'none' : 'block';
    document.querySelector(`.${buttonClass}`).setAttribute('aria-expanded', !isOpen);
    listContainer.setAttribute('aria-hidden', isOpen);
}

function openWindow(path){
    window.open(path ,target="_self")
}