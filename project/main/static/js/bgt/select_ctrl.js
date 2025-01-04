document.addEventListener("DOMContentLoaded", () => {
    const selectableElements = document.querySelectorAll(".selectable");
    const header = document.getElementById("header")
    const ids = new Array() // each element (id,name,amount)
    selectableElements.forEach(element => {
        element.addEventListener("click", (event) => {
            if (event.ctrlKey) { // Check if Ctrl key is pressed
                element.classList.toggle("selected"); // Toggle selection
                header.style.display = "none"
                ids.push([element.dataset.id, element.dataset.name, element.dataset.amount])

            } else {
                // Deselect other elements if Ctrl is not pressed
                selectableElements.forEach(el => el.classList.remove("selected"));
                header.style.display = "flex"
            }
        });
    });
    const contextMenu = document.getElementById("contextMenu");

    // Show custom context menu on right-click
    document.addEventListener("contextmenu", (event) => {
        event.preventDefault(); // Prevent default context menu
        contextMenu.style.top = `${event.clientY}px`; // Position the menu
        contextMenu.style.left = `${event.clientX}px`;
        contextMenu.style.display = "block"; // Show the menu
    });

    // Hide the context menu on click elsewhere
    document.addEventListener("click", () => {
        contextMenu.style.display = "none";
    });

    // QR generation
    const gnrQRbtn = document.getElementById("generateQRS");
    gnrQRbtn.addEventListener("click", (e) => {
        document.getElementById("contents").style.display = "none";
        // showing header --> active line bellow
        // document.getElementBy/Id("header").style.display = "flex";

        const all_qrs = document.createElement('div')
        all_qrs.id = "qrs";
        document.body.appendChild(all_qrs);

        ids.forEach(el => {
            // el[0] -> id, el[1] -> name, el[2] -> amount
            // for each drug, amount of qrs generated is equal to purchase amount
            const amount_needed = el[2]
            for (i = 0; i < amount_needed; i++) {

                // for each QR, a container
                const wholeContainer = document.createElement("div")
                // setting the class
                wholeContainer.classList.add("wholePhoto")
                // just photo
                const qrPhoto = document.createElement("div")
                qrPhoto.innerHTML = "";
                new QRCode(qrPhoto, {
                    text: el[0] + "_" + el[1],
                    width: 100, // Width of the QR code
                    height: 100, // Height of the QR code
                    colorDark: "#000000", // QR code color
                    colorLight: "#ffffff", // Background color
                    correctLevel: QRCode.CorrectLevel.H
                })
                const title = document.createElement('div')
                title.classList.add("qr-name")
                title.innerText = el[1]; // name
                wholeContainer.appendChild(qrPhoto);
                wholeContainer.appendChild(title);
                qrs.appendChild(wholeContainer);

            }

        })
        // deletion handling

    })

});