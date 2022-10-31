$('.plus-cart').click(function(){
    var id=$(this).attr("pid").toString();
    var eml=this.parentNode.parentNode.children[1].children[0]
    var unittotal=this.parentNode.parentNode.parentNode.parentNode.children[4]
    console.log(id)
    $.ajax({
        type:"GET",
        url:"/pluscart",
        data:{
            prod_id:id

        },
        success:function(data){

            eml.innerText = data.quantity
            unittotal.innerText = data.unit_total_price
            document.getElementById("subtotal").innerText = data.amount
            document.getElementById("totalamount").innerText = data.total_amount
            document.getElementById("total_amount").value = data.total_amount;
            document.getElementById("total_amount_sent").value = data.total_amount;
            document.getElementById("subtotal_amount_sent").value= data.amount;

        }
    });

});


$('.minus-cart').click(function(){
    var id=$(this).attr("pid").toString();
    var eml=this.parentNode.parentNode.children[1].children[0]
    var unittotal=this.parentNode.parentNode.parentNode.parentNode.children[4]
    console.log(id)
    $.ajax({
        type:"GET",
        url:"/minuscart",
        data:{
            prod_id:id

        },
        success:function(data){

            eml.innerText = data.quantity
            unittotal.innerText = data.unit_total_price
            document.getElementById("subtotal").innerText = data.amount
            document.getElementById("totalamount").innerText = data.total_amount
            document.getElementById("total_amount").value = data.total_amount;
            document.getElementById("total_amount_sent").value = data.total_amount;
            document.getElementById("subtotal_amount_sent").value= data.amount;

        }
    });

});