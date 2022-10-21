const searchField = document.querySelector('#searchField')
const tableOutput = document.querySelector('#table-output')
const tabledefaultOutput = document.querySelector('#expenses-current-table')
const paginationContainer = document.querySelector('.pagination-container')
const searchTableBody = document.querySelector('.searchTableBody')

tableOutput.style.display='none'

searchField.addEventListener('keyup', (e) => {

    const searchValue = e.target.value;
    if(searchValue.trim().length > 0){ // console.log('searchValue',searchValue)

        paginationContainer.style.display='none'

        searchTableBody.innerHTML=""
        fetch("/search-expenses",{
            body:JSON.stringify({ searchText: searchValue }), // You need to stringify the request data or objects for easy sending over the network
                    method:"POST", 
        })//fetch returns a promise , that we need to mapp to JSON
        .then((res) => res.json())//map it to json
        .then((data) => {//this returns another promise that has the data 
            console.log("data",data) 
            tabledefaultOutput.style.display='none'
            tableOutput.style.display='block'
            paginationContainer.style.display='block'

                if(data.length === 0){
                    tableOutput.innerHTML = `<p>No data found</p>`
                } else{
                    data.forEach(item=>{
                        searchTableBody.innerHTML+=`
                        <tr>
                            <td>${item.amount}</td>
                            <td>${item.category}</td>
                            <td>${item.description}</td>
                            <td>${item.owner}</td>
                            <td>Edit Delete</td>
                        </tr>
                        `
                    });
                }
        });
    }
    else{
        tableOutput.style.display='none'
        tabledefaultOutput.style.display='block';
        paginationContainer.style.display='block';

    }
});