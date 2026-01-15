import 'package:flutter/material.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';
import 'package:supabase_flutter/supabase_flutter.dart';
import 'package:go_router/go_router.dart';

import 'screens/auth/login_screen.dart';
import 'screens/auth/signup_screen.dart';
import 'screens/home/dashboard_screen.dart';
import 'screens/portfolio/portfolio_screen.dart';
import 'screens/portfolio/portfolio_management_screen.dart';
import 'screens/wealth/wealth_screen.dart';
import 'screens/wealth/wealth_management_screen.dart';
import 'screens/trends/trends_screen.dart';
import 'screens/analytics/analytics_screen.dart';

void main() async {
  WidgetsFlutterBinding.ensureInitialized();

  // Initialize Supabase with hardcoded credentials for release build
  await Supabase.initialize(
    url: 'https://hrlzrirsvifxsnccxvsa.supabase.co',
    anonKey:
        'eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6ImhybHpyaXJzdmlmeHNuY2N4dnNhIiwicm9sZSI6ImFub24iLCJpYXQiOjE3NjQ5NDQzMTcsImV4cCI6MjA4MDUyMDMxN30.IAhjGmpcNA9KIi6fSTIPauVVNTIRSb8jBNCJTpmHodA',
  );

  runApp(const ProviderScope(child: PortfolioAnalyzerApp()));
}

class PortfolioAnalyzerApp extends ConsumerWidget {
  const PortfolioAnalyzerApp({super.key});

  @override
  Widget build(BuildContext context, WidgetRef ref) {
    final router = GoRouter(
      initialLocation: '/login',
      redirect: (context, state) {
        final isLoggedIn = Supabase.instance.client.auth.currentUser != null;
        final isLoggingIn = state.matchedLocation == '/login' ||
            state.matchedLocation == '/signup';

        if (!isLoggedIn && !isLoggingIn) {
          return '/login';
        }
        if (isLoggedIn && isLoggingIn) {
          return '/';
        }
        return null;
      },
      routes: [
        GoRoute(
          path: '/login',
          builder: (context, state) => const LoginScreen(),
        ),
        GoRoute(
          path: '/signup',
          builder: (context, state) => const SignupScreen(),
        ),
        GoRoute(
          path: '/',
          builder: (context, state) => const DashboardScreen(),
        ),
        GoRoute(
          path: '/portfolio',
          builder: (context, state) => const PortfolioScreen(),
        ),
        GoRoute(
          path: '/portfolio/manage',
          builder: (context, state) => const PortfolioManagementScreen(),
        ),
        GoRoute(
          path: '/wealth',
          builder: (context, state) => const WealthScreen(),
        ),
        GoRoute(
          path: '/wealth/manage',
          builder: (context, state) => const WealthManagementScreen(),
        ),
        GoRoute(
          path: '/trends',
          builder: (context, state) => const TrendsScreen(),
        ),
        GoRoute(
          path: '/analytics',
          builder: (context, state) => const AnalyticsScreen(),
        ),
      ],
    );

    return MaterialApp.router(
      title: 'Portfolio Analyzer',
      theme: ThemeData(
        colorScheme: ColorScheme.fromSeed(
          seedColor: Colors.blue,
          brightness: Brightness.dark,
        ),
        useMaterial3: true,
        scaffoldBackgroundColor: Colors.black,
        appBarTheme: const AppBarTheme(
          backgroundColor: Colors.black,
          foregroundColor: Colors.white,
        ),
      ),
      routerConfig: router,
      debugShowCheckedModeBanner: false,
    );
  }
}
