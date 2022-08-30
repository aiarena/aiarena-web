import { Component, OnInit } from '@angular/core';

@Component({
  selector: 'app-finance',
  template: '<iframe style="height: 100%; width: 100%;" src="https://docs.google.com/spreadsheets/d/1wm_oZYPZv6t8urGtOCJ1yFtYjq-9WBixJQqaXQ7kiNc/edit#gid=1303247903"></iframe>',
  styles: ['']
})
export class FinanceComponent implements OnInit {

  constructor() { }

  ngOnInit(): void {
  }

}
