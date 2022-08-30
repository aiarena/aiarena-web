import { NgModule } from '@angular/core';
import { RouterModule, Routes } from '@angular/router';
import {FinanceComponent} from "./finance/finance.component";

const routes: Routes = [
  { path: 'finance', component: FinanceComponent },
];

@NgModule({
  imports: [RouterModule.forRoot(routes)],
  exports: [RouterModule]
})
export class AppRoutingModule { }
