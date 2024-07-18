const dishes = [];
  
function addDish() {
  const dishSelect = document.getElementById('dish');
  const selectedDish = dishSelect.options[dishSelect.selectedIndex];
  const dishId = selectedDish.value;
  const dishName = selectedDish.text;
  const dishPrice = parseFloat(selectedDish.getAttribute('data-price'));
  const quantity = parseInt(document.getElementById('quantity').value);
  
  const dish = {
    id: dishId,
    name: dishName,
    price: dishPrice,
    quantity: quantity
  };
  
  dishes.push(ddish);
  updateOrderList();
}

function updateOrderList() {
  const orderList = document.getElementById('order-list');
  orderList.innerHTML = '';
  let total = 0;
  
  dishes.forEach(dish => {
    const listItem = document.createElement('li');
    listItem.className = 'list-group-item';
    listItem.textContent = `${dish.name} - Cantidad: ${dish.quantity} - Precio: $${(dish.price * dish.quantity).toFixed(2)}`;
    orderList.appendChild(listItem);
    total += dish.price * dish.quantity;
  });
  
  const totalItem = document.createElement('li');
  totalItem.className = 'list-group-item active';
  totalItem.textContent = `Total: $${total.toFixed(2)}`;
  orderList.appendChild(totalItem);
}

function placeOrder() {
  fetch('{{ url_for("orders.create_order") }}', {
    method: 'POST',
    headers: {
      'Content-Type': 'application/json'
    },
    body: JSON.stringify({ dishes })
  }).then(response => {
    if (response.ok) {
      alert('Pedido realizado con éxito');
      window.location.reload();
    } else {
      alert('Hubo un problema al realizar el pedido');
    }
  });
}