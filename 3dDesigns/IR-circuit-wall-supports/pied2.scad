module triangle(x,y) {
    polygon(points=[[0,0],[x,0],[x,y]]);
}

x=30;
y=22;

linear_extrude(height=4) {
    
    difference() {
        triangle(x,y);
        
        S=(y-3)/y;
        {scale([S, S, S]) translate([8.5,3,0]) { triangle(x,y);}
        translate([18,0,0]) square(40);
        }
    }
    
    rotate(atan(y/x)) difference() {
        square([3,2]);
        translate([1.5,0,0]) {square([1.5, 0.5]);} 
    }

}
