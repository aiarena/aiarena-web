
// export { default } from "next-auth/middleware";

//default uses the _http-secure-cookie to check if a user is logged in.
// Use this to enforce unauthenticated pages on signin/signup

// export const config = {
//   matcher: ["/profile/:path*", "/settings", "/uploads", "/note/:path*"],
// };
// import { withAuth } from "next-auth/middleware"
import { NextResponse } from "next/server";
import type { NextRequest } from "next/server";
export async function middleware(req: NextRequest) {
  return NextResponse.next();
}


// import { withAuth } from "next-auth/middleware"
// import { NextResponse } from "next/server";
// import type { NextRequest } from "next/server";

// import { getToken } from "next-auth/jwt";

// const forced_authenticated_pages = ["/note", "/profile", "/settings", "/login"];
// const forced_unauthenticated_pages = ["/123", "/profile", "auth/signin"];



// split the route using /, then check for *

// export async function middleware(req: NextRequest) {
//   const path = req.nextUrl.pathname;

//   const token = await getToken({
//     req,
//     // cookieName: nextAuthCookieName,
//     secret: process.env.NEXTAUTH_SECRET,
//   });


//   if(!token) {
//     console.log("no token")
//   }
//   if (token) {
//     console.log("a token")
//   }


    //if authenticated and on a forced authenticated page
  // if (cookie && forced_authenticated_pages.includes(path)) {
  //   return NextResponse.redirect("http://localhost:3000/auth/signin");
  //   // return NextResponse.next();
  // }
    //if NOT authenticated and on a forced UN_authenticated page
  // if (!cookie && forced_unauthenticated_pages.includes(path)) {
  //   return NextResponse.next();
  // }

  // if (!token && forced_authenticated_pages.includes(path)) {
  //   return NextResponse.redirect("http://localhost:3000/auth/signin");
  // }

  // // Unauthenticated user trying to access pages meant for authenticated users
  // if (cookie && forced_unauthenticated_pages.includes(path)) {
  //   // if (!session && forced_authenticated_pages.includes(path)) {
  //   return NextResponse.redirect("http://localhost:3000/dashboard");
  // }
  // Default to allowing access
//   return NextResponse.next();
// }

// More on how NextAuth.js middleware works: https://next-auth.js.org/configuration/nextjs#middleware
// export default withAuth({
//   secret: process.env.NEXTAUTH_SECRET,
//   callbacks: {
//     authorized({ req, token }) {
//       const path = req.nextUrl.pathname;

//       if (!token && forced_authenticated_pages.includes(path)) {
//         return false
//       }
//       if (token && forced_unauthenticated_pages.includes(path))
//       {
//         return NextResponse.redirect('/dashboard');
//       }
//       return true //(authorized for this page)
//      },
//   },

//   //redirect to this if return is false (not authorized -> login), or if error (-> error)
//   pages: {
//     signIn: '/auth/signin',
//     error: '/auth/error',
//   }
// })













































// // import { withAuth } from "next-auth/middleware"
// import { NextResponse } from "next/server";
// import type { NextRequest } from "next/server";

// import { getToken } from "next-auth/jwt";

// const forced_authenticated_pages = ["/note", "/profile", "/settings", "/login"];
// const forced_unauthenticated_pages = ["/123", "/profile", "auth/signin"];

// type PathPattern = string;

// // function isPathAuthorized(path: string, patterns: PathPattern[]): boolean {
// //   let pathSegments = path.split("/").filter(Boolean); // Removes empty segments

// //   for (let pattern of patterns) {
// //     let patternSegments = pattern.split("/").filter(Boolean);

// //     if (pattern.endsWith(":path*")) {
// //       // Check if the static parts of the pattern match and if the URL has more segments than the pattern
// //       if (
// //         patternSegments
// //           .slice(0, -1)
// //           .every((seg, index) => seg === pathSegments[index]) &&
// //         pathSegments.length > patternSegments.length - 1
// //       ) {
// //         return true;
// //       }
// //     } else if (path === pattern) {
// //       return true;
// //     }
// //   }

// //   return false;
// // }

// const patterns: PathPattern[] = ["/about", "/store/:path*"];

// // split the route using /, then check for *

// export async function middleware(req: NextRequest) {
//   const path = req.nextUrl.pathname;
//   console.log(path);

//   const token = await getToken({
//     req,
//     // cookieName: nextAuthCookieName,
//     secret: process.env.NEXTAUTH_SECRET,
//   });

//   if (!token) {
//     console.log("no token");
//   }
//   if (token) {
//     console.log("token");
//   }

//   // if (isPathAuthorized(req.nextUrl.pathname, patterns)) {
//   //   // Proceed with the request
//   //   console.log("Authorized!");
//   // } else {
//   //   // Handle unauthorized access (e.g., send a 403 Forbidden response)
//   //   console.log("Unauthorized!");
//   //   return NextResponse.redirect("http://localhost:3000/auth/signin");
//   // }

//   //if authenticated and on a forced authenticated page
//   // if (cookie && forced_authenticated_pages.includes(path)) {
//   //   return NextResponse.redirect("http://localhost:3000/auth/signin");
//   //   // return NextResponse.next();
//   // }
//   //if NOT authenticated and on a forced UN_authenticated page
//   // if (!cookie && forced_unauthenticated_pages.includes(path)) {
//   //   return NextResponse.next();
//   // }

//   // if (!token && forced_authenticated_pages.includes(path)) {
//   //   return NextResponse.redirect("http://localhost:3000/auth/signin");
//   // }

//   // // Unauthenticated user trying to access pages meant for authenticated users
//   // if (cookie && forced_unauthenticated_pages.includes(path)) {
//   //   // if (!session && forced_authenticated_pages.includes(path)) {
//   //   return NextResponse.redirect("http://localhost:3000/dashboard");
//   // }
//   // Default to allowing access
//   return NextResponse.next();
// }

// // More on how NextAuth.js middleware works: https://next-auth.js.org/configuration/nextjs#middleware
// // export default withAuth({
// //   secret: process.env.NEXTAUTH_SECRET,
// //   callbacks: {
// //     authorized({ req, token }) {
// //       const path = req.nextUrl.pathname;

// //       if (!token && forced_authenticated_pages.includes(path)) {
// //         return false
// //       }
// //       if (token && forced_unauthenticated_pages.includes(path))
// //       {
// //         return NextResponse.redirect('/dashboard');
// //       }
// //       return true //(authorized for this page)
// //      },
// //   },

// //   //redirect to this if return is false (not authorized -> login), or if error (-> error)
// //   pages: {
// //     signIn: '/auth/signin',
// //     error: '/auth/error',
// //   }
// // })
