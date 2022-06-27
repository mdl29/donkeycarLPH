//cube([35,35,35]);

$fn = 70;

difference() {
    cube([100,100,48], center=true);
    cylinder(50, r1=35,r2=35, center=true);
    translate([0,-35,0]) {
        cube([70,70,50], center=true);
    }
}
translate([39,0,0]) {
    rotate([0,90,30])
        cylinder(69, r1=10,r2=18);
}
