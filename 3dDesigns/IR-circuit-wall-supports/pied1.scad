module triangle(x,y) {
    polygon(points=[[0,0],[x,0],[x,y]]);
}

linear_extrude(height=4) {
    
    difference() {
        triangle(22,30);
        
        {scale([0.8, 0.8, 0.8]) translate([5.5,3,0]) { triangle(22,30);}
        translate([14,0,0]) square(40);
        }
    }
    
    rotate(atan(30/22)) difference() {
        square([3,2]);
        translate([1.5,0,0]) {square([1.5, 0.5]);} 
    }

}
